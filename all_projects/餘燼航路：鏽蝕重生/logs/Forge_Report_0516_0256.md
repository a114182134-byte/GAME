# 鍛造報告

執行需求：改成Node2D 這腳本主要是人物本體的碰撞

你好，我是《餘燼航路：鏽蝕重生》的首席架構師。既然我們決定將 `player_ontology.gd` 轉型為 `Node2D`，這代表我們正式將「實體本體（Ontology）」與「物理碰撞（Collision）」進行深度綁定，這能確保角色在鏽蝕廢土上的位移與偵測更加精準。

以下是針對本次架構調整的技術規範：

### 1. 檔案功能說明

為了維持架構的擴充性，建議將原本「單一巨型腳本」拆分為模組化結構：

*   **`player_ontology.gd` (繼承 `CharacterBody2D`)**:
    *   **核心功能**：作為「本體節點」，負責處理基礎物理運動 (`move_and_slide`)、動量計算以及碰撞後的邊緣反應。
    *   **地位**：它是玩家角色的根節點（Root），必須掛載 `CollisionShape2D`。
*   **`input_handler.gd` (繼承 `Node`)**:
    *   **核心功能**：僅負責將鍵盤/搖桿輸入轉換為向量 (`direction`)，不處理任何物理邏輯。
*   **`state_machine.gd` (繼承 `Node`)**:
    *   **核心功能**：管理角色狀態（如：Idle, Walk, Dash, Scavenge），透過狀態模式切換對應的動畫與邏輯行為。
*   **`collision_sensor.gd` (繼承 `Area2D`)**:
    *   **核心功能**：作為 `player_ontology` 的子節點，負責「感知」而非「物理碰撞」。例如：感應鏽蝕物資或陷阱範圍。

---

### 2. 關聯性架構 (Composition over Inheritance)

我們採取「組合優於繼承」的策略，以確保《餘燼航路》的系統能靈活替換：

*   **依賴注入方向**：`player_ontology` 作為控制器，主動調用 `input_handler` 獲取輸入，並根據 `state_machine` 返回的結果更新 `velocity`。
*   **訊息傳遞**：
    *   `input_handler` -> (`Vector2`) -> `player_ontology`。
    *   `player_ontology` -> (`StateName`) -> `state_machine`。
*   **物理層級**：`player_ontology` 負責 `CharacterBody2D` 的硬碰撞（牆壁、障礙物）；`collision_sensor` 負責 `Area2D` 的軟偵測（互動物）。這樣做能避免一個 `CollisionShape2D` 同時處理太多邏輯導致的 bug。

---

### 3. Godot 對接注意事項 (必讀)

轉換為 `Node2D` (實質為 `CharacterBody2D`) 時，必須注意以下細節，否則角色會「鬼畜」或「穿牆」：

1.  **物理層級（Collision Layers/Masks）設定**：
    *   在 Godot 的 Inspector 中，務必定義好 Layer（本體屬於哪一層，例如：`Player`）與 Mask（本體會偵測哪一層，例如：`World` 與 `Enemy`）。不要設為全選，會導致效能消耗。
2.  **`_physics_process(delta)` 與 `_process(delta)` 的區分**：
    *   所有的移動相關計算（`velocity` 賦值與 `move_and_slide()`）**嚴格限制**在 `_physics_process` 中執行。
    *   UI 更新、動畫偵測等視覺效果放在 `_process`。
3.  **節點階層規範**：
    *   `CharacterBody2D` (PlayerRoot)
        *   `Sprite2D` (本體貼圖)
        *   `CollisionShape2D` (核心碰撞，**必須存在**)
        *   `AnimationPlayer` (狀態控制)
        *   `Node` (InputHandler)
        *   `Node` (StateMachine)
4.  **座標對齊**：
    *   確保 `Sprite2D` 的 `Offset` 與 `CollisionShape2D` 的中心對齊。在開發《餘燼航路》的複雜地形時，若偏移了 0.5 像素，會導致角色在過窄的平台邊緣卡住。
5.  **建議棄用舊式 `KinematicBody2D` 方法**：
    *   如果你是從舊版 Godot 升級，確保使用 `move_and_slide()` 而不是舊的 `move_and_slide(velocity)`。現在的邏輯是直接修改 `velocity` 屬性即可。

**首席架構師建議**：請立即建立 `player_ontology.gd` 的模板，並將原本的碰撞計算邏輯移至 `physics_process` 中。若遇到 `CharacterBody2D` 與 `Area2D` 偵測衝突，請使用 `Signal` 進行訊號解耦。

開始執行。如果你在 `move_and_slide` 的向量計算上遇到困難，隨時回報。