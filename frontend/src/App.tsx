import useIsMobile from "./useIsMobile";

import { Navigate, Route, HashRouter as Router, Routes } from "react-router";
import Artists from "./Artists/Artists";
import Labels from "./Labels/Labels";

const App = () => {
  const isMobile = useIsMobile();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/labels" />}></Route>
        <Route path="/artists" element={<Artists />}></Route>
        <Route path="/artists/:artistId" element={<Artists />}></Route>
        <Route path="/labels" element={<Labels />}></Route>
      </Routes>
    </Router>
  );
};

export default App;
