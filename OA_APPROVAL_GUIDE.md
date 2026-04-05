# OA Approval 系統安裝與使用指南

## 系統概述

OA Approval 是一個簡易型 OA 審核系統 (MVP)，支援：
- 動態表單模板設定
- 線性審核流程
- 下拉選單動態顯示
- 審核紀錄查看
- 郵件通知功能 (佇列處理)

## 系統需求

- **作業系統**: Linux/macOS/Windows
- **Python**: 3.11 或更高版本
- **PostgreSQL**: 14 或更高版本
- **RAM**: 至少 2GB
- **磁碟空間**: 至少 5GB

## 快速安裝

### 1. 建立新資料庫並安裝模組

```bash
# 停止現有 Odoo 服務
pkill -f "python.*odoo-bin"

# 刪除舊資料庫
psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo19;"

# 建立新資料庫
psql -U odoo -d postgres -c "CREATE DATABASE odoo19 OWNER odoo ENCODING 'UTF8';"

# 安裝模組
source venv/bin/activate
python odoo/odoo-bin -c odoo.conf -d odoo19 -i oa_approval --stop-after-init --without-demo=all

# 驗證安裝
python verify_oa_approval.py
```

### 2. 啟動 Odoo 服務

```bash
# 使用啟動腳本
./start.sh

# 或手動啟動
source venv/bin/activate
python odoo/odoo-bin -c odoo.conf
```

### 3. 訪問系統

- **URL**: http://127.0.0.1:8069
- **管理員帳號**: admin
- **預設密碼**: admin

## 功能驗證

### 自動驗證腳本

```bash
python verify_oa_approval.py
```

檢查項目：
- ✓ 模組已安裝
- ✓ 權限群組已建立
- ✓ 管理員已加入 OA 群組
- ✓ 基礎資料完整
- ✓ 選項資料正確

### 手動驗證步驟

1. **檢查模組狀態**
   ```sql
   SELECT state, latest_version FROM ir_module_module WHERE name = 'oa_approval';
   ```

2. **檢查權限群組**
   ```sql
   SELECT id, name::text FROM res_groups WHERE name::text LIKE '%OA%';
   ```

3. **檢查基礎資料**
   ```sql
   SELECT 'Form Categories' as item, COUNT(*) FROM oa_form_category
   UNION ALL
   SELECT 'Form Templates', COUNT(*) FROM oa_form_template
   UNION ALL
   SELECT 'Approval Chains', COUNT(*) FROM oa_approval_chain;
   ```

## 移植到其他機器

### 使用導出腳本

```bash
# 執行導出腳本
./export_for_porting.sh
```

導出內容：
- `oa_approval_porting_*.dump` - 資料庫備份
- `oa_approval_porting_*_module.tar.gz` - 模組源碼
- `oa_approval_porting_*_odoo.conf` - 配置文件
- `README_PORTING.txt` - 移植說明

### 在新機器上安裝

1. **設置環境**
   ```bash
   # 安裝系統依賴
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip postgresql postgresql-server-dev-all

   # 複製 Odoo 源碼
   git clone -b 19.0 https://github.com/odoo/odoo.git
   cd odoo

   # 建立虛擬環境
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **設置資料庫**
   ```bash
   # 建立 Odoo 用戶
   sudo -u postgres createuser -d -P odoo

   # 建立資料庫
   sudo -u postgres createdb -O odoo odoo19
   ```

3. **解壓縮模組**
   ```bash
   mkdir -p custom_addons
   tar -xzf oa_approval_porting_*_module.tar.gz -C custom_addons/
   ```

4. **調整配置**
   ```bash
   # 複製配置文件
   cp oa_approval_porting_*_odoo.conf odoo.conf

   # 編輯 addons_path
   vim odoo.conf
   # 確保包含: addons_path = custom_addons,odoo/addons,odoo/odoo/addons
   ```

5. **恢復資料庫**
   ```bash
   pg_restore -U odoo -h localhost -p 5432 -d odoo19 oa_approval_porting_*.dump
   ```

6. **啟動服務**
   ```bash
   source venv/bin/activate
   python odoo/odoo-bin -c odoo.conf
   ```

## 系統功能

### 1. 使用者權限

**三種權限群組：**
- **OA 用戶**: 可建立表單
- **OA 經理**: 可審核表單
- **OA 管理員**: 可設定系統參數

**管理員預設權限：**
- Administration 群組成員自動加入 OA 管理員和經理群組

### 2. 表單流程

**建立表單：**
1. 點選 "Create Form" 選單
2. 選擇表單類型（請假單/報銷單）
3. 填寫表單內容（下拉選單自動顯示相關選項）
4. 提交表單

**審核流程：**
1. 表單提交後，系統自動發送郵件通知審核者
2. 審核者可從 "All Forms" 選單查看待審核表單
3. 點選表單查看詳情並進行審核
4. 審核通過後自動進入下一關

### 3. 審核紀錄

**查看審核流程：**
1. 在表單詳情頁面，點選 "審核紀錄" 按鈕
2. 顯示完整的審核流程和當前狀態

### 4. 郵件通知

**通知類型：**
- 待審核通知
- 審核通過通知
- 審核駁回通知

**處理方式：**
- 使用 Odoo 內建郵件佇列
- 非同步發送，不影響使用者操作
- 由 cron 任務定期處理

## 系統維護

### 日常維護

```bash
# 查看系統日誌
tail -f logs/odoo.log

# 重啟服務
pkill -f "python.*odoo-bin"
./start.sh

# 備份資料庫
pg_dump -U odoo -h localhost -p 5432 -F c -f backup_$(date +%Y%m%d).dump odoo19
```

### 模組更新

```bash
# 更新模組
./start.sh -d odoo19 -u oa_approval

# 驗證更新
python verify_oa_approval.py
```

### 故障排除

**問題：模組未正確安裝**
```bash
# 強制重新安裝
python odoo/odoo-bin -c odoo.conf -d odoo19 -i oa_approval --stop-after-init
```

**問題：選項重複**
```sql
-- 清理重複選項
DELETE FROM oa_form_selection_option
WHERE id NOT IN (
    SELECT min(id) FROM oa_form_selection_option GROUP BY name, field_id
);
```

**問題：郵件未發送**
```bash
# 檢查郵件佇列
# 在 Odoo UI: 設置 > 技術 > 郵件 > 郵件佇列

# 手動處理郵件佇列
# 在 Odoo UI: 設置 > 排程任務 > Mail: Email Queue Manager
```

## 技術架構

### 模組結構

```
oa_approval/
├── models/                    # 資料模型
│   ├── oa_form_instance.py   # 表單實例
│   ├── oa_approval_step.py   # 審核步驟
│   └── ...
├── views/                     # 視圖定義
│   ├── oa_form_instance_views.xml
│   └── ...
├── wizards/                   # 精靈表單
│   ├── oa_form_wizard.py     # 表單建立精靈
│   └── ...
├── security/                  # 權限設定
│   ├── ir.model.access.csv   # 模型權限
│   └── ir_rule.xml           # 記錄規則
└── data/                      # 基礎資料
    ├── oa_approval_data.xml
    └── ...
```

### 資料模型

**核心模型：**
- `oa.form.category` - 表單類別
- `oa.form.template` - 表單模板
- `oa.form.field` - 表單字段
- `oa.form.instance` - 表單實例
- `oa.approval.chain` - 審核鏈
- `oa.approval.step` - 審核步驟
- `oa.approval.record` - 審核記錄

### 關鍵功能實現

**動態下拉選單：**
- 使用 `Many2one` 字段配合 `domain` 過濾
- 精靈中為每個選擇字段建立專用關聯字段

**審核流程：**
- 線性流程，依序經過各審核步驟
- 支援特定審核者和通用角色（直屬長官/部門經理）

**郵件通知：**
- 使用 `mail.mail` 模型
- 非同步佇列處理
- 支援 HTML 模板

## 版本資訊

- **版本**: 19.0.1.0.0
- **Odoo**: 19.0 Community Edition
- **Python**: 3.11+
- **PostgreSQL**: 14+

## 支援與反饋

如遇問題或需要技術支援，請：
1. 檢查系統日誌 `logs/odoo.log`
2. 運行驗證腳本 `verify_oa_approval.py`
3. 查看移植說明 `oa_approval_export/README_PORTING.txt`

---

**文檔版本**: 1.0
**最後更新**: 2026-04-05
**適用版本**: OA Approval 19.0.1.0.0
