# 鍛造報告

執行需求：增加sprite 這腳本主要是人物本體的碰撞 人物的圖片目前沒有 我自己拖圖進去

作為《餘燼航路：鏽蝕重生》（Ember Route: Rust Rebirth）的首席架構師，針對 `player_ontology.tscn`（玩家本體本體論/基礎架構）的擴充，我制定了以下架構優化方案。

為了達成「人物本體碰撞」與「視覺呈現」的解耦，我們必須嚴格遵循 **Godot 的場景節點樹規範**。

---

### 1. 檔案功能說明 (Architecture Breakdown)

我們將採取「實體分離」架構，確保碰撞邏輯與視覺表現互不干擾。

*   **`player_ontology.tscn` (主場景)**: 
    *   作為根節點（建議使用 `CharacterBody2D`），它是遊戲邏輯的載體。
    *   **責任**: 處理物理移動邏輯、輸入監聽、狀態機（State Machine）。
*   **`CollisionShape2D` (物理層)**: 
    *   掛載於主場景下。
    *   **責任**: 定義碰撞區域。建議使用 `CapsuleShape2D`，能精確匹配站立與蹲下時的碰撞需求。
*   **`Sprite2D` / `AnimatedSprite2D` (視覺層)**:
    *   **責任**: 負責顯示 PNG 圖片。
    *   **注意**: 請將此節點設定為 `Player` 節點的子節點。它只負責「呈現」，不參與物理計算。
*   **`player_controller.gd` (邏輯腳本)**:
    *   掛載於 `CharacterBody2D` 根節點。
    *   **責任**: 橋接輸入與物理運動。

---

### 2. 關聯性分析 (Dependency Mapping)

架構設計必須確保「牽一髮而動全身」時的穩定性：

1.  **物理與視覺的從屬關係**:
    *   `CharacterBody2D` (Root) -> `Sprite2D`
    *   `CharacterBody2D` (Root) -> `CollisionShape2D`
    *   *關係說明*: 當根節點移動時，Sprite 與碰撞盒會同步跟隨，確保視覺與物理碰撞不脫節。
2.  **腳本與節點的連結**:
    *   在 `player_controller.gd` 中，使用 `@onready var sprite = $Sprite2D` 來獲取視覺控制權（例如翻轉圖片 `sprite.flip_h`）。
3.  **封裝原則**:
    *   Sprite 不應包含移動邏輯；`player_ontology` 不應包含具體的動畫切換邏輯（建議交給 `AnimationPlayer` 或 `AnimationTree`）。

---

### 3. Godot 對接注意事項 (Implementation Best Practices)

在將你的 PNG 拖入 Godot 時，請務必遵循以下「鏽蝕重生」開發標準：

*   **Z-Index (渲染層級)**:
    *   在 `Sprite2D` 的屬性面板中，確保 `Z-Index` 設定正確。如果你的遊戲有場景遮擋，務必將玩家的 `Z-Index` 設為高於背景層。
*   **Offset (偏移量調整)**:
    *   匯入圖片後，圖片中心點（Offset）預設在圖片中心。請根據你的碰撞盒位置調整 `Sprite2D` 的 `Offset`，確保視覺上的「腳底」對齊物理上的「地面」。
*   **Texture Filtering (材質濾鏡)**:
    *   如果是像素風格，在 `Import` 面板中將 `Filter` 改為 `Nearest`（防止圖片模糊）。設定後別忘了按下 **Reimport**。
*   **Collision Layer/Mask (碰撞分層)**:
    *   在 `CharacterBody2D` 的 `Collision` 屬性中，設定 `Layer` (我是什麼) 與 `Mask` (我要撞誰)。這能大幅優化效能並避免不必要的誤判。
*   **物件重用性 (Inheritance)**:
    *   建議將 `player_ontology.tscn` 設為「可繼承場景」。未來若有 NPC 或敵人，可以繼承此場景來擴充不同的視覺 Sprite，但共用相同的物理架構。

---

**首席架構師建議：**
下一步操作時，請先將 `Sprite2D` 拖入後，透過「修改 `CollisionShape2D` 的形狀」來契合圖片輪廓，而不是強行修改圖片大小。**物理邊界是遊戲的靈魂，視覺只是它的皮囊。**

準備好後，請進行拖曳操作，若出現 `Transform` 對位問題，請隨時回報。