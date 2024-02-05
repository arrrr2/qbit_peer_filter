用于过滤吸血客户端。使用 qbittorrent Web API 。  
会定期检查，ban 掉并记录。  
用法：```python main.py```

### 配置文件 config.yaml
|名称|用途|
|--|--|
|filter_path|每一个规则文件的路径|
|filter_order|规则文件的顺序|
|webui_url|webui 的地址，通常为 ip:port|
|username|用户名|
|password|密码|


### 规则文件
|名称|用途|值|例|
|-|-|-|-|
|list_type|满足过滤规则的 peer 是被 ban 还是放行|black, white|black|
|multi_rules_behavior|同一文件下多条规则是需要全部满足还是任意一个|intersection (同时满足), union (任一)|intersection|
|cycle|检查时间，单位为秒|300 (默认)|120|
|client_filter|判断客户端名称的方式|regex, keyword, exact_match|keyword|
|client_expression|判断依据||devel|
|ip|符合要求的 ip 范围||['192.168.1.1', '192.168.1.233']|
|uploaded_portion|已上传数据量占种子总大小之比||0.75|
|uploaded_size|已上传数据量，单位为 GByte||3|

<br>
  
* * * 
Used for filtering leeching clients. Utilizes the qBittorrent Web API.  
Regularly checks, bans, and logs offending peers.  
Usage: ```python main.py```

### Configuration file config.yaml
|Name|Purpose|
|--|--|
|filter_path|Path for each rule file|
|filter_order|Order of the rule files|
|webui_url|Address of the webui, usually ip:port|
|username|Username|
|password|Password|


### Rule file
|Name|Purpose|Value|Example|
|-|-|-|-|
|list_type|Whether peers meeting the filter criteria are to be banned or allowed|black, white|black|
|multi_rules_behavior|Whether multiple rules in the same file need to be all met or just any|intersection (all), union (any)|intersection|
|cycle|Check time, in seconds|300 (default)|120|
|client_filter|Method to judge client names|regex, keyword, exact_match|keyword|
|client_expression|Basis for judgment||devel|
|ip|IP range that meets the criteria||['192.168.1.1', '192.168.1.233']|
|uploaded_portion|Ratio of uploaded data to total size of the torrent||0.75|
|uploaded_size|Amount of data uploaded, in GBytes||3|
