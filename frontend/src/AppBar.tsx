import Box from "@mui/joy/Box";
import Typography from "@mui/joy/Typography";

export interface AppBarProps {
  title: string;
}

const AppBar = ({ title }: AppBarProps) => {
  return (
    <>
      <Box
        bgcolor={(theme) => theme.palette.primary.darkChannel}
        height={80}
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
      >
        <Typography color="primary" level="h1">
          {title}
        </Typography>
      </Box>
      <Box height={64} mb={2} pt={2} width="100%"></Box>
    </>
  );
};

export default AppBar;
