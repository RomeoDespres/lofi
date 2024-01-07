import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import Box from "@mui/joy/Box";
import Tooltip from "@mui/joy/Tooltip";
import { ReactNode } from "react";

export interface InfoIconProps {
  text: ReactNode;
}

const InfoIcon = ({ text }: InfoIconProps) => {
  return (
    <Tooltip
      title={
        <Box display="flex" flexDirection="column" gap={1}>
          {text}
        </Box>
      }
      sx={{ maxWidth: 400 }}
    >
      <HelpOutlineIcon fontSize="small" />
    </Tooltip>
  );
};

export default InfoIcon;
