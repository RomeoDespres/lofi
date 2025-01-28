import { useEffect, useState } from "react";
import { DefaultService, Labels } from "../../api";
import useIsMobile from "../../useIsMobile";
import LabelsTableDesktop from "./LabelsTableDesktop";
import LabelsTableMobile from "./LabelsTableMobile";

const LabelsTable = () => {
  const [labels, setLabels] = useState<Labels>();
  const isMobile = useIsMobile();

  useEffect(() => {
    DefaultService.getLabels().then(setLabels);
  }, []);

  const labelsTableProps = { labels };

  if (isMobile) return <LabelsTableMobile {...labelsTableProps} />;
  else return <LabelsTableDesktop {...labelsTableProps} />;
};

export default LabelsTable;
