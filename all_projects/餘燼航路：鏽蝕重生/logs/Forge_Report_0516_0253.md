# 鍛造報告

執行需求：改成Area2D 這腳本主要是偵測區

身為《餘燼航路：鏽蝕重生》的首席架構師，針對 `player_detect.gd` 的重構需求，將其從單純的邏輯類轉換為 `Area2D` 節點組件，是為了更好地利用 Godot 的物理引擎進行「空間觸發」與「層級碰撞」。

以下是重構後的技術架構說明：

---

### 1. 檔案功能說明 (Architectural Modules)

在新的架構下，我們將偵測邏輯拆解為三個核心層次：

*   **`player_detect.gd` (Area2D Component):** 
    *   **核心職責：** 作為「感知器」。它不再負責處理邏輯，僅負責維護一個 `body_entered` 與 `body_exited` 的狀態機，回報「偵測到目標」的訊號。
*   **`detector.tscn` (Scene File):** 
    *   **核心職責：** 封裝了 `Area2D` 與 `CollisionShape2D`。首席架構師要求：必須預設將 `CollisionLayer` 設定為 `DetectionLayer`，並將 `CollisionMask` 指向 `PlayerLayer`，確保效能優化（僅檢測特定圖層）。
*   **`interactable_controller.gd` (Logic Handler):** 
    *   **核心職責：** 作為「決策者」。監聽來自 `player_detect` 的訊號，決定是否觸發 UI 互動、陷阱啟動或敵方 AI 狀態變更。

---

### 2. 檔案關聯性 (Module Dependencies)

採用 **「訊號驅動設計 (Signal-Driven Design)」** 以確保解耦：

1.  **實體化關係：** 任何需要偵測功能的物體（如：偵測陷阱、NPC 警戒範圍），將 `detector.tscn` 作為子節點加入。
2.  **依賴注入：** `player_detect.gd` 不應知道父節點的存在，它僅透過 `emit_signal("player_found", body)` 發送廣播。
3.  **事件流：** 
    *   `Player` 進入 `Area2D` -> `player_detect` 觸發 `body_entered`。
    *   `player_detect` 發出自定義訊號 `player_in_range`。
    *   父節點（如 `EnemyAI` 或 `TriggerZone`）捕獲訊號，執行相應的 `Logic`。

---

### 3. Godot 對接注意事項 (Implementation Best Practices)

這是執行本次鍛造的核心紅線，請務必嚴格遵守：

*   **Collision Layer/Mask 設定（防禦性開發）：**
    *   在 `_ready()` 中執行 `self.collision_layer = 0`，避免偵測器本身參與不必要的物理碰撞（如推擠玩家）。
    *   確保 `CollisionMask` 只勾選 `Player` 的圖層，減少 Physics Engine 的計算壓力。
*   **物理同步問題：**
    *   若玩家在偵測區內被刪除或改變狀態，請務必手動檢查 `has_overlapping_bodies()`，避免 `body_exited` 訊號未被觸發導致偵測器「卡死」在偵測狀態。
*   **Deferred Call (延遲調用)：**
    *   在 `Area2D` 的訊號回調中，**嚴禁**直接進行場景切換或刪除節點。若需進行複雜邏輯，務必使用 `call_deferred()`，以免導致引擎在物理幀內崩潰。
*   **封裝組件化 (Composition over Inheritance)：**
    *   將 `player_detect.gd` 寫成一個 `Class_name` 為 `PlayerDetector` 的節點。這樣在編輯器中，設計師可以直接透過 Inspector 調整 `monitoring` 屬性，而無需更動程式碼。

---

**首席架構師叮嚀：**
「在《餘燼航路》的世界裡，效能與準確性同樣重要。這次轉換為 `Area2D` 後，請確保每個偵測器的 `Shape` 都盡量使用 `CircleShape2D` 或 `RectangleShape2D`，並避免使用複雜的多邊形形狀，這是保持鏽蝕世界運作順暢的關鍵。」

**準備好實作了嗎？需要我為你草擬 `player_detect.gd` 的核心程式碼框架嗎？**