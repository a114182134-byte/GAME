# 鍛造報告

執行需求：增加sprite 這腳本主要是人物本體的碰撞 要有人物的圖片

作為《餘燼航路：鏽蝕重生》（Ember Route: Rust Reborn）的首席架構師，針對 `player_ontology.tscn`（玩家本體本體論場景）的擴充，我制定了以下技術規範。

為了實現「帶有碰撞與視覺表現」的玩家節點，我們將採用 **Godot 組合式架構**。

---

### 1. 檔案功能說明

建議將原有的單一檔案拆解為以下三個核心組件，以符合專案的模組化需求：

*   **`player_ontology.tscn` (主場景)**：
    *   作為 **容器 (Container)**，根節點使用 `CharacterBody2D`。
    *   負責掛載腳本邏輯與物理屬性。
*   **`player_sprite.tscn` (視覺元件)**：
    *   使用 `AnimatedSprite2D` 或 `Sprite2D`。
    *   獨立處理動畫序列（如：鏽蝕後的機械運轉、緩慢行走）。
    *   將視覺層與物理層分離，方便未來替換「外骨骼裝甲」或「不同角色外觀」。
*   **`player_controller.gd` (控制腳本)**：
    *   掛載於 `CharacterBody2D`。
    *   處理輸入映射 (Input Map)、移動向量計算以及與碰撞體之間的交互。

---

### 2. 組件關聯性 (Dependency Graph)

架構層級如下：

1.  **`CharacterBody2D` (根)**
    *   **`CollisionShape2D` (物理)**：定義人物的碰撞範圍（判定盒）。
    *   **`PlayerSprite` (場景實例)**：作為根節點的子節點。
        *   *關聯：* 透過節點路徑 (NodePath) 或腳本引用，讓 `player_controller.gd` 在執行 `move_and_slide()` 時，同步觸發 `PlayerSprite` 的動畫狀態機（如 `play("walk")`）。

---

### 3. Godot 對接注意事項

在進行 `player_ontology` 的擴充與實作時，請務必遵守以下規範，以確保遊戲運行的穩定性：

*   **物理與圖層 (Collision Layers & Masks)**：
    *   **Layer 設定**：請將 `player_ontology` 的物理層設為 `Player`，Mask 設為 `World` 與 `Enemies`。
    *   **避免穿模**：確保 `CollisionShape2D` 的大小略小於 `Sprite2D` 的視覺邊界，以符合《餘燼航路》廢土風格中角色與環境交互的「紮實感」。
*   **動畫同步 (Animation State Machine)**：
    *   不要在 `Sprite` 腳本中直接處理輸入邏輯。應由 `player_controller.gd` 發送訊號或呼叫方法（例如 `update_animation(velocity)`）來變更 `Sprite` 狀態，保持職責單一原則。
*   **像素對齊 (Pixel Snap)**：
    *   如果遊戲是像素美術風格，請在專案設定中開啟 `Rendering/2D/Snap/Snap 2d transforms to pixel`。這能防止人物移動時出現「畫面抖動」或「邊緣破碎」的視覺瑕疵。
*   **預製件封裝 (Instancing)**：
    *   請務必將 `Sprite` 以場景的形式掛載，而非直接在根場景中添加節點。這樣當未來美術資源更新（例如角色鏽蝕程度加深）時，只需修改 `player_sprite.tscn`，所有實例化的場景將自動同步，避免在主場景中進行繁瑣的重複作業。

---

**首席架構師叮嚀：**
「在鏽蝕重生的世界裡，碰撞體就是玩家與這片荒原互動的唯一準則。務必確保 `CollisionShape2D` 的邊界精確，不要讓任何一個像素的誤判，導致玩家墜入荒原的虛空。」

下一步請著手建立 `CollisionShape2D` 節點，並將預設 Sprite 貼圖掛載上去。完成後通知我，我們將進行移動邏輯的接入。