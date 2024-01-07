import Input from "@mui/joy/Input";
import textMatchesQuery from "./LabelsTable/textMatchesQuery";
import useIsMobile from "./useIsMobile";

const SearchBar = () => {
  const isMobile = useIsMobile();

  const handleChange = (value: string) => {
    const defaultDisplay = isMobile ? "flex" : "table-row";
    for (const node of document.getElementsByClassName("lofi-label-row")) {
      (node as any).style.display = textMatchesQuery(node.id, value)
        ? defaultDisplay
        : "none";
    }
  };

  return (
    <Input
      placeholder="Search"
      onChange={(event) => handleChange(event.target.value)}
      sx={{ display: "flex", flexGrow: 1 }}
    />
  );
};

export default SearchBar;
