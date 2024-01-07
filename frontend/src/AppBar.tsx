import Box from "@mui/joy/Box";
import Typography from "@mui/joy/Typography";
import SearchBar from "./SearchBar";
export interface AppBarProps {
  onChangeSearchQuery: (query: string) => void;
  searchQuery: string | undefined;
  title: string;
}

const AppBar = ({ onChangeSearchQuery, searchQuery, title }: AppBarProps) => {
  return (
    <>
      <Box
        alignItems="center"
        bgcolor={(theme) => theme.palette.background.level1}
        display="flex"
        height={80}
        justifyContent="space-between"
        left={0}
        p={2}
        position="fixed"
        sx={{
          backdropFilter: "blur(10px)",
          borderBottomColor: (theme) => theme.palette.divider,
          borderBottomStyle: "solid",
        }}
        top={0}
        width="100%"
        zIndex={100}
      >
        <Typography color="primary" level="h1">
          {title}
        </Typography>
        <Box display="flex" gap={2}>
          <SearchBar onChange={onChangeSearchQuery} value={searchQuery} />
        </Box>
      </Box>
      <Box height={64} mb={2} pt={2} width="100%"></Box>
    </>
  );
};

export default AppBar;
