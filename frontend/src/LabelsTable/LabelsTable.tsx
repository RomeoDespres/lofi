import { useEffect, useMemo, useState } from "react";
import { DefaultService, Labels } from "../api";
import useIsMobile from "../useIsMobile";
import LabelsTableDesktop from "./LabelsTableDesktop";
import LabelsTableMobile from "./LabelsTableMobile";
import textMatchesQuery from "./textMatchesQuery";

export interface LabelsTableProps {
  searchQuery: string;
}

const LabelsTable = ({ searchQuery }: LabelsTableProps) => {
  const [labels, setLabels] = useState<Labels>();
  const isMobile = useIsMobile();

  useEffect(() => {
    DefaultService.getLabels().then(setLabels);
  }, []);

  const searchedLabels = useMemo(
    () =>
      labels === undefined
        ? labels
        : {
            labels: labels.labels.filter((label) =>
              textMatchesQuery(label.name, searchQuery)
            ),
          },
    [labels, searchQuery]
  );

  const labelsTableProps = { labels: searchedLabels };

  if (isMobile) return <LabelsTableMobile {...labelsTableProps} />;
  else return <LabelsTableDesktop {...labelsTableProps} />;
};

export default LabelsTable;
