import Input from "@mui/joy/Input";

export interface SearchBarProps {
  onChange: (value: string) => void;
  value: string | undefined;
}

const SearchBar = ({ onChange, value }: SearchBarProps) => (
  <Input
    placeholder="Search"
    onChange={(event) => onChange(event.target.value)}
    value={value}
  />
);

export default SearchBar;
