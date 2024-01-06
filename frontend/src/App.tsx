import Box from "@mui/joy/Box";
import AppBar from "./AppBar";
import LabelsTable from "./LabelsTable";

const App = () => {
  return (
    <Box bgcolor="#101418" padding={2}>
      <AppBar title="lofi labels" />
      <LabelsTable />
    </Box>
  );
};

export default App;
