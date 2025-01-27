import Page from "../Page";
import useIsMobile from "../useIsMobile";
import LabelsTable from "./LabelsTable";
import textMatchesQuery from "./LabelsTable/textMatchesQuery";

export default function Labels() {
  const isMobile = useIsMobile();
  return (
    <Page
      onSearch={(value: string) => {
        const defaultDisplay = isMobile ? "flex" : "table-row";
        for (const node of document.getElementsByClassName("lofi-label-row")) {
          (node as any).style.display = textMatchesQuery(node.id, value)
            ? defaultDisplay
            : "none";
        }
      }}
      title="lofi labels"
      titleLink="/labels"
    >
      <LabelsTable />
    </Page>
  );
}
