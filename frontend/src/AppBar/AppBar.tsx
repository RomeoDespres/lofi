import Box from "@mui/joy/Box";
import Grid from "@mui/joy/Grid";
import Typography from "@mui/joy/Typography";
import MobileSidebar from "../Sidebar/MobileSidebar";
import ContactButton from "./ContactButton";
import SearchBar from "./SearchBar";
export interface AppBarProps {
  onSearch: (query: string) => void;
  title: string;
}

const AppBar = ({ onSearch, title }: AppBarProps) => {
  return (
    <>
      <Grid
        alignItems="center"
        bgcolor={(theme) => theme.palette.background.level1}
        container
        display="flex"
        height={{ md: 80, xs: 144 }}
        justifyContent="space-between"
        left={0}
        p={2}
        pb={{ md: 2, xs: 1 }}
        position="fixed"
        spacing={1}
        sx={{
          backdropFilter: "blur(10px)",
          borderBottomColor: (theme) => theme.palette.divider,
          borderBottomStyle: "solid",
        }}
        top={0}
        width="100%"
        zIndex={100}
      >
        <Grid>
          <Box alignItems="center" display="flex" gap={2}>
            <MobileSidebar />
            <Typography color="primary" level="h1">
              {title}
            </Typography>
          </Box>
        </Grid>

        <Grid md={3} xs={12}>
          <Box display="flex" gap={2}>
            <SearchBar onSearch={onSearch} />
            <ContactButton />
          </Box>
        </Grid>
      </Grid>
      <Box height={{ md: 80 - 16, xs: 144 - 16 }} mb={2} pt={2} width="100%"></Box>
    </>
  );
};

export default AppBar;
