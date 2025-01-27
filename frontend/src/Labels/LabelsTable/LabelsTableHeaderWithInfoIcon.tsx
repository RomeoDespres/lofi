import Box from "@mui/joy/Box";
import { ReactNode } from "react";
import InfoIcon from "./InfoIcon";

export interface LabelsTableHeaderWithInfoIconProps {
  header: string;
  info?: ReactNode;
  justify?: "center" | "flex-start" | "flex-end";
}

const LabelsTableHeaderWithInfoIcon = ({
  header,
  info,
  justify = "flex-end",
}: LabelsTableHeaderWithInfoIconProps) => (
  <Box
    alignItems="center"
    display="flex"
    gap={1}
    height="100%"
    justifyContent={justify}
  >
    <Box whiteSpace="wrap">{header}</Box>
    {info === undefined ? null : <InfoIcon text={info} />}
  </Box>
);

export default LabelsTableHeaderWithInfoIcon;
