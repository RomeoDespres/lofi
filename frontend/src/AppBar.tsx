import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import Box from "@mui/joy/Box";
import IconButton from "@mui/joy/IconButton";
import Typography from "@mui/joy/Typography";
import useScrollTrigger from "@mui/material/useScrollTrigger";
export interface AppBarProps {
  title: string;
}

const AppBar = ({ title }: AppBarProps) => {
  const scrollTrigger = useScrollTrigger({ disableHysteresis: true });
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
        <Box sx={{ opacity: scrollTrigger ? 1 : 0, transition: "opacity 0.3s" }}>
          <IconButton onClick={() => window.scrollTo(0, 0)}>
            <ArrowUpwardIcon />
          </IconButton>
        </Box>
      </Box>
      <Box height={64} mb={2} pt={2} width="100%"></Box>
    </>
  );
};

export default AppBar;
