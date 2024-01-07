import { ClickAwayListener } from "@mui/base/ClickAwayListener";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import Box from "@mui/joy/Box";
import Tooltip from "@mui/joy/Tooltip";
import { ReactNode, useState } from "react";

export interface InfoIconProps {
  text: ReactNode;
}

const InfoIcon = ({ text }: InfoIconProps) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <ClickAwayListener onClickAway={() => setShowTooltip(false)}>
      <Tooltip
        leaveTouchDelay={10000}
        onClose={() => setShowTooltip(false)}
        onOpen={() => setShowTooltip(true)}
        open={showTooltip}
        title={
          <Box display="flex" flexDirection="column" gap={1}>
            {text}
          </Box>
        }
        sx={{ maxWidth: 400 }}
      >
        <HelpOutlineIcon fontSize="small" onClick={() => setShowTooltip(true)} />
      </Tooltip>
    </ClickAwayListener>
  );
};

export default InfoIcon;
