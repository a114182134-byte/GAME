# 鍛造報告

執行需求：改成CharacterBody2D 這腳本主要是人物本體的碰撞

你好，我是《餘燼航路：鏽蝕重生》的首席架構師。

將 `player_ontology.gd` 從一個通用的邏輯容器轉型為基於 `CharacterBody2D` 的物理實體，是我們引擎底層優化與物理交互規範化的關鍵一步。這意味著我們將不再依賴 `Area2D` 或自定義的邏輯位移，而是正式接入 Godot 的 `PhysicsServer2D` 系統。

以下是本次重構的架構說明：

---

### 1. 檔案功能規劃 (模組化設計)

為了維持《餘燼》代碼庫的擴展性，我們將功能解耦為以下三個核心檔案：

*   **`player_body.gd` (繼承 `CharacterBody2D`)**
    *   **核心職責**：作為本體的「物理門面」。處理 `_physics_process` 的執行、`move_and_slide()` 的調用，以及與世界碰撞邊界的數據交換。
*   **`player_controller.gd` (繼承 `Node`)**
    *   **核心職責**：輸入處理。將玩家的 `Input` 轉化為「意圖向量」（如：移動向量 `velocity`、攻擊指令），將這些數據傳遞給 `player_body`。
*   **`player_state_machine.gd` (繼承 `Node`)**
    *   **核心職責**：狀態機管理。負責處理腳本生命週期中的狀態切換（如：Idle, Move, Dash, Dying），確保物理行為符合當前遊戲狀態。

---

### 2. 檔案關聯性 (架構圖)

數據流向採取**單向依賴原則**，防止循環引用導致的記憶體洩漏：

1.  **控制器層 (`PlayerController`)**：作為入口，捕獲輸入，呼叫 `player_body` 設置速度參數。
2.  **狀態層 (`PlayerStateMachine`)**：監控 `player_body` 的狀態（如 `is_on_floor()`），並決定下一幀允許的行為。
3.  **本體層 (`PlayerBody`)**：底層執行者，負責輸出最終物理運算結果。

**關聯模式：**
`Controller` -> `StateMachine` -> `Body` (最終執行)。
所有腳本透過 `Signals` 或 `Composition` (組合) 進行交互，避免直接 `get_parent()` 耦合。

---

### 3. Godot 對接注意事項 (關鍵執行清單)

在轉移至 `CharacterBody2D` 時，請務必執行以下檢查：

*   **碰撞層級 (Collision Layers & Masks)**：
    *   務必在編輯器中明確定義 `Layer` (我是什麼) 與 `Mask` (我能撞到誰)。建議將玩家設為單獨的 Layer，避免與環境產生不必要的複雜物理計算。
*   **移動與速度計算 (`velocity`)**：
    *   `CharacterBody2D` 內置了 `velocity` 屬性，請直接使用它。
    *   **重要提示**：在 `_physics_process` 中調用 `move_and_slide()` 之前，必須確保 `velocity` 已歸一化並乘上速度乘數，否則在斜坡上會出現移動不一致。
*   **物理幀率穩定性**：
    *   確保所有涉及到位移的邏輯都放置在 `_physics_process` 中，而非 `_process`。這對於《餘燼航路》的精密戰鬥手感至關重要。
*   **緩存機制**：
    *   若玩家本體需要調用 `RayCast2D` 或 `ShapeCast2D` 進行地面檢測（如：斜坡補正），請確保在 `_ready()` 階段預先取得節點引用，避免在物理幀循環中進行 `get_node()` 操作，這會造成效能瓶頸。
*   **重力應用 (`gravity`)**：
    *   請從 `ProjectSettings` 獲取默認重力，並根據鏽蝕世界的環境設定添加自定義重力係數，不要寫死 `980` 這個數值。

---

**首席架構師結語：**
這次重構後，請確保 `player_body.gd` 的腳本開頭嚴格遵循以下格式，以便引擎進行類型檢查：

```gdscript
class_name PlayerBody extends CharacterBody2D

# 核心物理屬性定義
@export var movement_speed: float = 300.0
@export var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
```

準備好後即可開始移植，若在處理 `CollisionShape2D` 的動態調整時遇到瓶頸，隨時向我匯報。**為了鏽蝕世界的重生，我們不容許任何物理抖動。**