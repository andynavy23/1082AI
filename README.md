# 1082AI
## 以Heroku建立課程助教聊天機器人

### 功能：
 - 雲端執行（Heroku）
 - 連接資料庫（Mongodb）
 - 聊天記錄LOG
 - 特定條件下主動傳送訊息
 - 回復規則（package：exec）

### 開發環境與工具：
 - Mac Pro（開發電腦）
 - Python（程式語言）
 - Mongodb（資料庫連接）
 - Heroku（雲端託管執行）
 - Ngrok（本地開發測試）
 - Lin BOT（聊天機器人框架）
 - Robo 3T（資料庫GUI介面）

### 相關套件（可以參考 requirements.txt）：
 - Flask
 - line-bot-sdk
 - pymongo
 - requests
 - gunicorn

### 資料庫格式（Heroku 擴充功能 mLab MongoDB）：
 - users（Collection）
    - groupID（群組ID）
    - userID（使用者ID）
    - display_name（使用者名稱）
    - picture_url（使用者大頭照圖片連結）
    - status_message（使用者狀態內容）
    - join_datetime（加入使用者資料時間點）
 - groups（Collection）
    - groupID（群組ID）
    - datetime（加入群組時間點）
 - rules（Collection）
    - keyword（觸發規則關鍵字）
    - rule（規則）
    - output（輸出結果）
 - log（Collection）
    - userID（使用者ID）
    - messageID（說話內容ID）
    - text（說話內容）
    - message_type（說話類型：text、img、video．．．）
    - source_type（說話來源類型：user、group）
    - datetime（說話紀錄時間點）

### Demo：
1. 在 Heroku 上創建好資料庫後於本地端使用GUI連接確認後續資料有無更新
    - GUI畫面  
    ![創建資料庫](/img/創建資料庫.png)

2. 邀請機器人加入LINE課程群組，機器人會分辨是否加入過此群組同時通知管理者加入一個群組。
     - 加入群組會先在群組裡面跟大家打招呼  
     ![加入群組打招呼](/img/加入群組打招呼.png)
     - 將groupID、datetime加入資料庫（groups），並且發送訊息給管理者  
     ![通知管理者加入群組](/img/通知管理者加入群組.png)

3. 透過「報到」指令抓取使用者資料加入資料庫（users）
     - 使用者給予「報到」指令  
     ![使用者給予報到指令]](/img/使用者給予報到指令.png)
     - 機器人判斷說話內容為「報到」指令抓取userID等資訊加入資料庫  
     ![機器人將使用者資料加入資料庫](/img/機器人將使用者資料加入資料庫.png)
     - 機器人比對是否報導過，提醒使用者不用重複報到  
     ![機器人提醒重複報導](/img/機器人提醒重複報導.png)

4. 查看資料庫是否有資料匯入
    - GUI畫面  
    ![資料庫更新](/img/資料庫更新.png)
