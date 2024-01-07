import Box from "@mui/joy/Box";
import AppBar from "./AppBar";
import LabelsTable from "./LabelsTable";
import useIsMobile from "./useIsMobile";

const App = () => {
  const isMobile = useIsMobile();
  return (
    <Box bgcolor="#101418" padding={isMobile ? 1 : 2}>
      <AppBar title="lofi labels" />
      <LabelsTable />
    </Box>
  );
};

export default App;
