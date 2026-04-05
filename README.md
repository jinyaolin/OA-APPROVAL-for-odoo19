# OA Approval System for Odoo 19

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-green.svg)](https://www.odoo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)

一個功能完整的 OA 審核系統，專為 Odoo 19 設計。支援動態表單模板、線性審核流程、郵件通知等企業級功能。

## ✨ 主要功能

### 📋 動態表單系統
- **表單類別管理** - 彈性組織不同類型的表單
- **表單模板設定** - 可視化配置表單字段和規則
- **動態字段生成** - 支援文字、日期、下拉選單等多種字段類型
- **草稿編輯** - 支援草稿階段修改表單內容

### 🔍 智能下拉選單
- **動態過濾** - 根據字段類型自動顯示相關選項
- **選項管理** - 集中管理下拉選單選項
- **防止重複** - 確保選項資料完整性

### ✅ 審核工作流
- **線性審核流程** - 依序經過各審核節點
- **彈性配置** - 支援特定審核者或角色審核（直屬長官/部門經理）
- **審核記錄** - 完整的審核歷史追蹤
- **狀態管理** - 實時顯示表單審核狀態

### 👥 權限管理
- **三級權限系統**
  - **OA 用戶** - 可建立和查看自己的表單
  - **OA 經理** - 可審核表單
  - **OA 管理員** - 可設定系統參數和模板
- **自動權限分配** - 管理員自動獲得 OA 權限

### 📧 郵件通知
- **非同步發送** - 使用郵件佇列，不影響使用者操作
- **多種通知類型** - 待審核、審核通過、審核駁回
- **HTML 模板** - 精美的郵件樣式

## 🚀 快速開始

### 系統需求

- **Python**: 3.11 或更高版本
- **PostgreSQL**: 14 或更高版本
- **Odoo**: 19.0 Community Edition
- **RAM**: 至少 2GB
- **磁碟空間**: 至少 5GB

### 安裝步驟

#### 1. 下載模組

```bash
# 克隆專案
git clone https://github.com/jinyaolin/OA-APPROVAL-for-odoo19.git
cd OA-APPROVAL-for-odoo19
```

#### 2. 設置 Odoo 環境

```bash
# 建立 Python 虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝 Odoo 依賴
pip install -r requirements.txt
```

#### 3. 配置資料庫

```bash
# 建立 PostgreSQL 用戶
sudo -u postgres createuser -d -P odoo

# 建立資料庫
sudo -u postgres createdb -O odoo odoo19
```

#### 4. 安裝模組

```bash
# 複製模組到 Odoo addons 目錄
cp -r custom_addons/oa_approval /path/to/odoo/addons/

# 更新 Odoo 配置文件，確保 addons_path 包含模組路徑
```

#### 5. 啟動 Odoo 並安裝

```bash
# 啟動 Odoo 並安裝模組
python odoo/odoo-bin -c odoo.conf -d odoo19 -i oa_approval
```

#### 6. 訪問系統

- **URL**: http://localhost:8069
- **管理員帳號**: admin
- **預設密碼**: admin

## 📚 文檔

詳細文檔請參考：

- **[完整使用指南](OA_APPROVAL_GUIDE.md)** - 詳細的安裝、配置和使用說明
- **[項目總結](PROJECT_SUMMARY.md)** - 功能列表和技術架構
- **[CLAUDE.md](CLAUDE.md)** - 開發指南和項目結構

## 🎯 使用範例

### 建立請假單

1. 點選「Create Form」選單
2. 選擇「請假單」模板
3. 填寫表單：
   - 選擇假別（事假、病假、產假等）
   - 設定起始和結束日期
   - 填寫請假原因
4. 提交表單

### 審核流程

1. 收到郵件通知
2. 登入系統查看待審核表單
3. 點選表單查看詳情
4. 選擇「通過」或「駁回」
5. 填寫審核意見（可選）
6. 確認審核

## 🏗️ 專案結構

```
oa_approval/
├── models/              # 資料模型
│   ├── oa_form_instance.py       # 表單實例
│   ├── oa_approval_step.py       # 審核步驟
│   ├── oa_form_selection_option.py  # 選項管理
│   └── ...
├── views/               # 視圖定義
│   ├── oa_form_instance_views.xml
│   └── ...
├── wizards/             # 精靈表單
│   ├── oa_form_wizard.py         # 表單建立精靈
│   └── ...
├── security/            # 權限設定
│   ├── ir.model.access.csv      # 模型權限
│   └── ir_rule.xml              # 記錄規則
└── data/                # 基礎資料
    ├── oa_approval_data.xml
    └── oa_form_selection_option_data.xml
```

## 🎨 支援的表單類型

### 請假單
- 假別選擇：事假、病假、產假、特休、婚假、喪假、陪產假
- 日期設定
- 請假原因說明

### 報銷單
- 報銷類型：交通費、誤餐費、辦公用品、客戶招待費、其他
- 金額輸入
- 報銷事由說明

## 🔧 技術架構

- **後端**: Python 3.11+, Odoo 19 ORM
- **前端**: Odoo Web Client (JavaScript, QWeb)
- **資料庫**: PostgreSQL 14+
- **郵件**: Odoo Mail 模組（非同步佇列處理）

## 🐛 故障排除

### 模組未正確安裝
```bash
# 強制重新安裝
python odoo/odoo-bin -c odoo.conf -d odoo19 -i oa_approval --stop-after-init
```

### 選項顯示重複
```sql
-- 清理重複選項
DELETE FROM oa_form_selection_option
WHERE id NOT IN (
    SELECT min(id) FROM oa_form_selection_option GROUP BY name, field_id
);
```

### 檢查系統狀態
```bash
# 使用驗證腳本
python verify_oa_approval.py
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 本專案
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 開發規範

- 遵循 Odoo 編碼規範
- 添加適當的文檔字串
- 編寫測試用例
- 保持提交訊息清晰

## 📄 許可證

本專案採用 LGPL-3 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

**jinyaolin**

## 🙏 致謝

- Odoo 社群
- 所有貢獻者

## 📞 聯絡方式

- **GitHub**: [@jinyaolin](https://github.com/jinyaolin)
- **Email**: jinyao.lin@gmail.com

## 🗺️ 路線圖

### 已完成 ✅
- [x] 動態表單系統
- [x] 線性審核流程
- [x] 權限管理
- [x] 郵件通知
- [x] 智能下拉選單
- [x] 審核記錄追蹤

### 計劃中 🚧
- [ ] 並行審核流程
- [ ] 條件審核路由
- [ ] 表單列印功能
- [ ] 統計報表
- [ ] 移動端優化
- [ ] 多語言支援

---

**注意**: 本專案為 MVP 版本，持續開發中。歡迎提供反饋和建議！

⭐ 如果這個專案對你有幫助，請給個 Star！
