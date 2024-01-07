import Box from "@mui/joy/Box";
import { useState } from "react";
import AppBar from "./AppBar";
import LabelsTable from "./LabelsTable";
import useIsMobile from "./useIsMobile";

const App = () => {
  const [searchQuery, setSearchQuery] = useState<string>();

  const isMobile = useIsMobile();

  return (
    <Box bgcolor="#101418" padding={isMobile ? 1 : 2}>
      <AppBar
        onChangeSearchQuery={setSearchQuery}
        searchQuery={searchQuery}
        title="lofi labels"
      />
      <LabelsTable searchQuery={searchQuery ?? ""} />
    </Box>
  );
};

export default App;
