import Clear from "@mui/icons-material/Clear";
import IconButton from "@mui/joy/IconButton";
import Input from "@mui/joy/Input";
import React from "react";
import useIsMobile from "../useIsMobile";

export interface SearchBarProps {
  onSearch: (query: string) => void;
}

const SearchBar = ({ onSearch }: SearchBarProps) => {
  const [query, setQuery] = React.useState("");
  const isMobile = useIsMobile();

  function handleChange(value: string) {
    setQuery(value);
    onSearch(value);
  }

  return (
    <Input
      endDecorator={
        <IconButton onClick={() => handleChange("")}>
          <Clear />
        </IconButton>
      }
      onChange={(event) => handleChange(event.target.value)}
      onFocus={(event) => event.target.select()}
      placeholder="Search"
      sx={{ display: "flex", flexGrow: 1 }}
      value={query}
    />
  );
};

export default SearchBar;
