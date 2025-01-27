import Box from "@mui/joy/Box";
import AppBar from "./AppBar/AppBar";
import useIsMobile from "./useIsMobile";

export interface PageProps {
  onSearch: (query: string) => void;
  title: string;
}

export default function Page({
  children,
  title,
  onSearch,
}: React.PropsWithChildren<PageProps>) {
  const isMobile = useIsMobile();
  return (
    <>
      <Box bgcolor="#101418" padding={isMobile ? 1 : 2}>
        <AppBar onSearch={onSearch} title={title} />
        {children}
      </Box>
    </>
  );
}
