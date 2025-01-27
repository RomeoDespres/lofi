import Box from "@mui/joy/Box";
import React from "react";
import AppBar from "./AppBar/AppBar";
import useIsMobile from "./useIsMobile";

export interface PageProps {
  onSearch: (query: string) => void;
  pageTitle?: string | undefined;
  title: string;
  titleColor?: string | undefined;
  titleLink: string;
}

export default function Page({
  children,
  pageTitle,
  title,
  titleLink,
  titleColor,
  onSearch,
}: React.PropsWithChildren<PageProps>) {
  const isMobile = useIsMobile();

  React.useEffect(() => {
    document.title = pageTitle ?? title;
  }, [pageTitle, title]);

  return (
    <>
      <Box bgcolor="#101418" padding={isMobile ? 1 : 2}>
        <AppBar
          onSearch={onSearch}
          title={title}
          titleColor={titleColor}
          titleLink={titleLink}
        />
        {children}
      </Box>
    </>
  );
}
