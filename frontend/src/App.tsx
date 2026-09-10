import { Route, Routes } from "react-router-dom";

import { CorridorMapPage } from "./routes/CorridorMapPage";
import { StructurePlaceholderPage } from "./routes/StructurePlaceholderPage";

function App() {
  return (
    <Routes>
      <Route path="/packages/:packageId" element={<CorridorMapPage />} />
      <Route path="/structures/:structureId" element={<StructurePlaceholderPage />} />
    </Routes>
  );
}

export default App;
