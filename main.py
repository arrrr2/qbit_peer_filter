import qbittorrentapi
import re
import yaml
import ipaddress
import asyncio
import os
import logging


class torrent_status():
    def __init__(self, torrent, cli:qbittorrentapi.Client) -> None:
        self.cli = cli
        self.torrent_dict = {
            'downloaded_size': torrent.size, 
            'total_size': torrent.completed, 
            'hash': torrent.hash,
            'name': torrent.name, 
            'peers': []
        }
        self.get_peers()

    def get_peers(self):
        torrent = self.torrent_dict
        peers = self.cli.sync.torrentPeers(torrent['hash'])
        for idx, peer in peers.peers.items(): 
            peer_stat = {
                'peer_symbol': idx,
                'client_name': peer.client,
                'ip': peer.ip,
                'up_speed': peer.up_speed, 
                'progress': peer.progress, 
                'uploaded_size': peer.uploaded, 
                'flags': peer.flags
            }
            peer_stat['uploaded_portion'] = peer_stat['uploaded_size'] / torrent['total_size']
            torrent['peers'].append(peer_stat)


class filter():
    def __init__(self, config_path, cli:qbittorrentapi.Client) -> None:
        self.cli = cli
        with open(config_path, 'r', encoding='utf-8') as file:
            conf = yaml.safe_load(file)
            config = {}
            checklist = {}
            config['behave_multi'] = conf.get('multi_rules_behavior', 'intersection')
            config['list_type'] = conf.get('list_type', 'white')
            config['cycle'] = conf.get('cycle', 300)

            cf = conf.get('client_filter', None)
            if cf is not None:
                exp = conf.get('client_expression')
                if cf == 'regex':
                    checklist['reg'] = lambda x: re.match(exp, x)
                if cf == 'exact_match':
                    checklist['em'] = lambda x: exp == x
                else: 
                    checklist['kw'] = lambda x: exp in x

            cf = conf.get('ip', None)
            if cf is not None:
                start_ip = int(ipaddress.ip_address(cf[0]))
                end_ip = int(ipaddress.ip_address(cf[1]))
                checklist['ipr'] = lambda x: start_ip <= int(ipaddress.ip_address(x))  <= end_ip

            cf = conf.get('uploaded_size', None)
            if cf is not None:
                checklist['ups'] = lambda x: x > cf

            cf = conf.get('uploaded_portion', None)
            if cf is not None:
                checklist['upp'] = lambda x: x > cf

            self.checklist = checklist
            self.config = config

    def check(self, torrent:torrent_status):
        ck = self.checklist
        cf = self.config
        tor = torrent.torrent_dict
        peers = torrent.torrent_dict['peers']
        ban_list = []
        
        
        true_lambda = lambda x: True
        for peer in peers:    
            flag = True if cf['behave_multi'] == 'intersection' else False
            all_flags = []
            all_flags.append(ck.get('reg',true_lambda)(peer['client_name']))
            all_flags.append(ck.get('em',true_lambda)(peer['client_name']))
            all_flags.append(ck.get('kw',true_lambda)(peer['client_name']))
            all_flags.append(ck.get('ipr',true_lambda)(peer['ip']))
            all_flags.append(ck.get('ups',true_lambda)(peer['uploaded_size']))
            all_flags.append(ck.get('upp',true_lambda)(peer['uploaded_portion']))
            # print(all_flags)
            if cf['behave_multi'] == 'intersection':
                for f in all_flags: flag = flag and f
            else: 
                for f in all_flags: flag = flag or f

            # print(flag)
            # print("result ", flag == (cf['list_type'] == 'black'))
            if ((flag == (cf['list_type'] == 'black'))):ban_list.append(peer['peer_symbol']) 

        return ban_list 
    
    def ban_peers(self, banned_peers):
        qbcli = self.cli
        if len(banned_peers) != 0:
            logging.critical('ban peer: ' + str(banned_peers))
            print(banned_peers)
            qbcli.transfer_ban_peers(banned_peers)

        pass

    async def execute(self):
        qbcli = self.cli
        while True:
            torrents_downloading = qbcli.torrents.info.downloading()
            torrents_seeding = qbcli.torrents.info.seeding()
            all_banned_peers = []
            torrents_active = [torrents_downloading, torrents_seeding]
            for torrents in torrents_active:
                for torrent in torrents:
                    if torrent.upspeed == 0: continue
                    hash = torrent.hash
                    peers = qbcli.sync.torrentPeers(hash)
                    if len(peers.peers) == 0: continue
                    # print(len(peers.peers))
                    tst = torrent_status(torrent, qbcli)
                    # print(tst)
                    all_banned_peers += self.check(tst)
            self.ban_peers(all_banned_peers)
            await asyncio.sleep(self.config['cycle'])
        
        pass


async def main():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    qbcli = qbittorrentapi.Client(host=config.get('webui_url', 'localhost:8080'), 
                                  username=config.get('username', None),
                                  password=config.get('password', None))
    
    filters = [filter(os.path.join(config.get('filter_path', '.'), fname), qbcli) for fname in config.get('filter_order')]
    jobs = [asyncio.create_task(x.execute()) for x in filters]
    
    while True:
        await asyncio.sleep(10)

logging.basicConfig(filename='history.log', level=logging.CRITICAL,
                    format='%(asctime)s - %(levelname)s - %(message)s')


asyncio.run(main())