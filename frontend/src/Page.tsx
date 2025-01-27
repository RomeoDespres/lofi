import Box from "@mui/joy/Box";
import AppBar from "./AppBar/AppBar";
import useIsMobile from "./useIsMobile";

export interface PageProps {
  title: string;
}

export default function Page({ title, children }: React.PropsWithChildren<PageProps>) {
  const isMobile = useIsMobile();
  return (
    <>
      <Box bgcolor="#101418" padding={isMobile ? 1 : 2}>
        <AppBar title={title} />
        {children}
      </Box>
    </>
  );
}
