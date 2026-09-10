import { Route, Routes } from "react-router-dom";

import { CorridorMapPage } from "./routes/CorridorMapPage";
import { PileRecordPage } from "./routes/PileRecordPage";
import { StructureDetailPage } from "./routes/StructureDetailPage";

function App() {
  return (
    <Routes>
      <Route path="/packages/:packageId" element={<CorridorMapPage />} />
      <Route
        path="/packages/:packageId/structures/:structureId"
        element={<StructureDetailPage />}
      />
      <Route path="/packages/:packageId/piles/:pileId" element={<PileRecordPage />} />
    </Routes>
  );
}

export default App;
