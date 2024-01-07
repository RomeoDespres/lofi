import Box from "@mui/joy/Box";
import Typography from "@mui/joy/Typography";

export interface PopularityBarProps {
  height: number;
  max?: number;
  value: number;
  width: number;
}

const PopularityBar = ({ height, max = 100, value, width }: PopularityBarProps) => {
  const commonBoxProps = { borderRadius: 3, height };
  return (
    <Box alignItems="center" display="flex" gap={1}>
      <Typography>{value}</Typography>
      <Box
        bgcolor={(theme) => theme.palette.primary[900]}
        width={width}
        {...commonBoxProps}
      >
        <Box
          bgcolor={(theme) => theme.palette.primary[500]}
          width={`${(width * value) / max}px`}
          {...commonBoxProps}
        />
      </Box>
    </Box>
  );
};

export default PopularityBar;
