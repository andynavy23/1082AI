# 1082AI
## 聊天機器人
### 功能：
 - 雲端執行（Heroku）
 - 讀取資料庫（mongodb）（package：exec）
 - 輸出聊天記錄LOG檔
 - 群組中使用者ID
 - 主動推送訊息給群組
 - 特定條件下主動傳送訊息
### 資料庫：
 - users
    - groupID
    - userID
    - display_name
    - picture_url
    - status_message
    - join_datetime
 - groups
    - groupID
 - rules
    - keyword
    - rule
    - output
 - log
    - userID
    - messageID
    - text
    - message_type
    - source_type
    - datetime
