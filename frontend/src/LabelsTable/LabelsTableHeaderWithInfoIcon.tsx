import Box from "@mui/joy/Box";
import { ReactNode } from "react";
import InfoIcon from "./InfoIcon";

export interface LabelsTableHeaderWithInfoIconProps {
  header: string;
  info: ReactNode;
}

const LabelsTableHeaderWithInfoIcon = ({
  header,
  info,
}: LabelsTableHeaderWithInfoIconProps) => (
  <Box alignItems="center" display="flex" gap={1} justifyContent="flex-end">
    {header} <InfoIcon text={info} />
  </Box>
);

export default LabelsTableHeaderWithInfoIcon;
