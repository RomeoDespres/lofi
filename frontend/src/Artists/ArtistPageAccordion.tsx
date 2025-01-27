import Accordion from "@mui/joy/Accordion";
import AccordionDetails, { accordionDetailsClasses } from "@mui/joy/AccordionDetails";
import AccordionGroup from "@mui/joy/AccordionGroup";
import AccordionSummary, { accordionSummaryClasses } from "@mui/joy/AccordionSummary";

import ListItemContent from "@mui/joy/ListItemContent";
import Typography from "@mui/joy/Typography";

import Box from "@mui/joy/Box";
import useIsMobile from "../useIsMobile";

export interface ArtistPageAccordionProps {
  color: string | undefined;
  title: string;
}
export default function ArtistPageAccordion({
  children,
  color,
  title,
}: React.PropsWithChildren<ArtistPageAccordionProps>) {
  const isMobile = useIsMobile();

  return (
    <AccordionGroup
      transition="0.2s"
      sx={{
        borderRadius: isMobile ? 4 : 8,
        bgcolor: (theme) => theme.palette.background.level1,
        [`& .${accordionDetailsClasses.content}.${accordionDetailsClasses.expanded}`]: {
          paddingBlock: "1rem",
        },
        [`& .${accordionSummaryClasses.button}`]: {
          paddingBlock: "1rem",
        },
      }}
      component={Box}
    >
      <Accordion disabled={!isMobile} defaultExpanded>
        <AccordionSummary indicator={isMobile ? undefined : null}>
          <ListItemContent>
            <Typography level="h3" sx={{ color }}>
              {title}
            </Typography>
          </ListItemContent>
        </AccordionSummary>
        <AccordionDetails>{children}</AccordionDetails>
      </Accordion>
    </AccordionGroup>
  );
}
