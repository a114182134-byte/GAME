# 鍛造報告

執行需求：採用四段式代碼 input是輸入 output是輸出 ontology是本體 detect是偵測

各位同仁，

我很高興地向大家匯報，我們對「魚叉系統 (Harpoon System)」的模組化解耦鍛造工作已經圓滿完成。這批模組化組件 (`harpoon_input`, `harpoon_output`, `harpoon_ontology`, `harpoon_detect`) 將極大地提升我們「餘燼航路：鏽蝕重生」項目中目標偵測與數據處理系統的靈活性與可維護性。

這次重構嚴格遵循了我們最初提出的四段式架構：**輸入 (Input)**、**本體 (Ontology)**、**偵測 (Detect)**、**輸出 (Output)**。以下我將針對這批新模組進行詳細說明：

---

### 1. 每個檔案功能說明

每個模組都包含一個 `.gd` 腳本檔案和一個 `.tscn` 場景檔案。`.tscn` 在這裡通常作為該模組的邏輯容器或入口點，即使它可能只包含一個根 `Node`。

#### 1.1 `harpoon_input.gd` / `harpoon_input.tscn`
*   **功能描述：**
    *   **`harpoon_input.gd` (腳本):** 負責收集來自遊戲世界或玩家的原始數據和觸發事件。它是魚叉系統的「感知器」。這可能包括：
        *   玩家發出的掃描指令（按鍵、UI互動）。
        *   遊戲內環境感測器讀數（例如，區域掃描、射線投射結果）。
        *   定時器觸發的週期性掃描。
        *   來自其他系統的數據流，作為潛在的偵測目標。
    *   **`harpoon_input.tscn` (場景):** 通常是一個根 `Node` 或 `Timer`、`Area2D/3D` 等節點的容器，用於承載 `harpoon_input.gd` 腳本。它定義了觸發偵測的機制，例如，一個偵測半徑或一個掃描動畫的控制器。

#### 1.2 `harpoon_ontology.gd` / `harpoon_ontology.tscn`
*   **功能描述：**
    *   **`harpoon_ontology.gd` (腳本):** 作為魚叉系統的「知識庫」或「世界模型」。它定義了所有可被魚叉系統識別的目標類型、屬性、分類規則及其相互關係。這包括：
        *   可偵測物品的數據結構（例如：礦物、廢料、敵對實體、稀有遺跡）。
        *   每個目標的關鍵屬性（例如：價值、危險等級、所需採集工具、弱點）。
        *   分類標準和標籤系統。
        *   用於判斷目標優先級或行為模式的數據。
    *   **`harpoon_ontology.tscn` (場景):** 通常只是一個根 `Node` 作為 `harpoon_ontology.gd` 腳本的邏輯容器。因為它主要處理數據定義，不涉及複雜的視覺或互動組件。它可能加載或管理 `Resource` 類型資產，這些資產定義了具體的目標數據。

#### 1.3 `harpoon_detect.gd` / `harpoon_detect.tscn`
*   **功能描述：**
    *   **`harpoon_detect.gd` (腳本):** 是魚叉系統的「核心處理單元」。它接收來自 `harpoon_input` 的原始數據，並利用 `harpoon_ontology` 中定義的知識和規則，執行實際的目標偵測、識別和分析。這包括：
        *   對輸入數據進行過濾和預處理。
        *   執行空間查詢（如 `RayCast`、`Area2D/3D` 碰撞檢測）。
        *   根據 `ontology` 規則匹配潛在目標。
        *   對已識別目標進行進一步的屬性提取和狀態評估。
        *   將偵測結果（例如：目標列表、每個目標的詳細信息）發送給 `harpoon_output`。
    *   **`harpoon_detect.tscn` (場景):** 可以是一個根 `Node`，用於承載 `harpoon_detect.gd` 腳本。如果偵測機制涉及可視組件（如視覺偵測範圍），它也可能包含 `RayCast` 或 `Area` 節點。

#### 1.4 `harpoon_output.gd` / `harpoon_output.tscn`
*   **功能描述：**
    *   **`harpoon_output.gd` (腳本):** 負責將 `harpoon_detect` 的處理結果轉化為玩家可見的信息、遊戲內的實際效果或對其他系統的指令。它是魚叉系統的「執行器」和「報告器」。這包括：
        *   更新UI界面，顯示偵測到的目標列表、目標詳細信息。
        *   在遊戲世界中標記或突出顯示偵測到的目標。
        *   觸發音效、視覺特效。
        *   發送信號給其他遊戲系統（例如：告知採集系統「可採集資源已偵測到」、告知任務系統「發現任務目標」）。
        *   處理偵測失敗或異常情況的反馈。
    *   **`harpoon_output.tscn` (場景):** 可以是一個根 `Node`，用於承載 `harpoon_output.gd` 腳本。如果輸出直接涉及UI元素，它也可能包含 `Control` 節點（如 `Label`、`ProgressBar`）。

---

### 2. 網頁端自動掛載 (Auto-attach) 架構設計效益

這裡的「網頁端自動掛載」借鑒了Web開發中組件化和自動服務注入的概念，在Godot中，這主要對應於「單例 (Singleton) / 自動加載 (AutoLoad)」設計模式，或者是透過一個中央管理系統來自動實例化和連接這些模組。其核心效益在於：

1.  **高度模組化與解耦 (High Modularity & Decoupling):**
    *   每個模組職責單一，相互之間依賴關係清晰且鬆散。例如，`input` 只負責數據收集，不關心如何偵測或輸出。
    *   這使得系統更容易理解、修改和擴展，降低了修改一個部分對其他部分產生負面影響的風險。

2.  **可重用性 (Reusability):**
    *   各模組可以獨立存在或與其他系統組合。例如，`harpoon_ontology` 可能被其他掃描系統甚至AI行為樹重用，以統一對遊戲世界實體的認知。
    *   `harpoon_output` 也可能被改造成一個通用的信息顯示模組。

3.  **易於維護與偵錯 (Easier Maintenance & Debugging):**
    *   當問題出現時，可以快速定位到特定的模組，而不是在龐大的單一腳本中查找。
    *   每個模組可以獨立進行測試，提高了代碼的品質和可靠性。

4.  **促進團隊協作 (Facilitates Team Collaboration):**
    *   不同的開發者可以同時專注於不同的模組，減少了代碼衝突。例如，一名開發者負責 `input` 邏輯，另一名負責 `output` UI。

5.  **清晰的數據流 (Clear Data Flow):**
    *   強制實施了從 `input` -> `detect` (依賴 `ontology`) -> `output` 的單向數據流，使得系統的行為路徑清晰可預測。

6.  **可擴展性 (Scalability):**
    *   當我們需要增加新的偵測方式（例如，聲納偵測、熱成像），只需擴展或添加新的 `detect` 模組，而不需要修改核心 `input` 或 `output`。
    *   增加新的可偵測目標類型，只需更新 `ontology` 而不影響邏輯。

7.  **性能優化潛力 (Potential for Performance Optimization):**
    *   由於模組的獨立性，可以針對特定性能瓶頸的模組進行優化，例如，如果 `harpoon_detect` 的算法複雜，我們可以單獨對其進行重構或採用更高效的數據結構，而無需擔心影響其他部分。

---

### 3. Godot 載入後的注意事項

在 Godot 引擎中實現這種自動掛載和模組化架構時，我們需要注意以下幾點：

1.  **單例 (Singleton) / 自動加載 (AutoLoad) 的應用：**
    *   如果魚叉系統是一個全局且唯一的系統，那麼將 `harpoon_input.tscn`、`harpoon_ontology.tscn`、`harpoon_detect.tscn` 和 `harpoon_output.tscn` 作為 **自動加載場景 (AutoLoad Scene)** 註冊到項目設置中是最佳實踐。
    *   **優點：** 這些場景會在遊戲啟動時自動加載並添加到場景樹的根部，可以通過其節點名（例如 `HarpoonDetect`）全局訪問，無需手動 `instance()` 或 `add_child()`。
    *   **注意事項：**
        *   **加載順序：** 在項目設置的 AutoLoad 列表中，節點的順序決定了它們 `_ready()` 函數被調用的順序。如果模組之間存在嚴格的初始化依賴（例如 `detect` 需要 `ontology` 的數據才能初始化），則必須確保 `ontology` 在 `detect` 之前加載。
        *   **內存佔用：** 作為單例，這些模組將始終存在於內存中。確保其資源管理得當，避免不必要的內存浪費。
        *   **過度依賴：** 雖然全局訪問方便，但仍需避免讓每個模組直接訪問其他模組的內部細節。盡量通過 **信號 (Signals)** 進行通信，以保持解耦。

2.  **信號 (Signals) 傳遞與連接：**
    *   這是實現模組間鬆散耦合的關鍵。
    *   **示例：**
        *   `harpoon_input.gd` 可以定義 `scanned_triggered` 信號，當玩家觸發掃描時發出。
        *   `harpoon_detect.gd` 則監聽 `harpoon_input` 的 `scanned_triggered` 信號，並在收到後開始偵測。
        *   `harpoon_detect.gd` 偵測完成後，發出 `detection_results_ready(results: Dictionary)` 信號。
        *   `harpoon_output.gd` 監聽 `harpoon_detect` 的 `detection_results_ready` 信號，並根據 `results` 更新UI。
    *   **注意事項：** 在單例模式下，這些信號連接可以在每個模組的 `_ready()` 函數中完成（例如 `HarpoonInput.connect("scanned_triggered", self, "_on_scanned_triggered")`），因為它們都是全局可見的。

3.  **資源管理 (Resource Management)：**
    *   `harpoon_ontology.gd` 可能會加載自定義資源 (Custom Resources, `.tres` 或 `.res` 文件)，這些資源包含遊戲中可偵測對象的具體數據。
    *   **注意事項：** 確保這些資源的加載和卸載邏輯正確，特別是在需要動態加載大量數據或有多個 `ontology` 版本時。Godot 的 `ResourceLoader` 和 `ResourceSaver` 是管理這些資源的重要工具。

4.  **場景結構與節點生命週期：**
    *   雖然單例模式很常用，但如果某些模組（例如 `harpoon_input` 上的特定偵測區域或 `harpoon_output` 上的特定UI組件）需要在遊戲流程中動態創建、銷毀或依附於特定遊戲對象，那麼它們可能需要被設計為可實例化的子場景，由其他更高級的場景（如一個玩家飛船場景）來加載和管理。
    *   **注意事項：** 明確哪些模組是全局的、生命週期與遊戲綁定，哪些是局部的、生命週期與特定遊戲對象綁定，這有助於避免設計混亂。

5.  **錯誤處理與異常回報：**
    *   每個模組都應該有健壯的錯誤處理機制。例如，如果 `harpoon_input` 沒有接收到預期的數據，或者 `harpoon_detect` 無法匹配任何 `ontology` 條目，應有明確的回報機制（例如發出錯誤信號、記錄日誌或向 `harpoon_output` 報告失敗信息）。

---

這次的模組化重構是我們在構建複雜遊戲系統方面邁出的重要一步。它為我們提供了更強大的工具，來應對「餘燼航路：鏽蝕重生」中日益增長的系統複雜性。請各位開發者在後續工作中積極採用這些新模組，並在實踐中提供寶貴的反饋。

謝謝大家。

首席架構師 敬上