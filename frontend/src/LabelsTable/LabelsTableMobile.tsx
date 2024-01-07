import { ReactNode } from "react";

import OpenInNew from "@mui/icons-material/OpenInNew";
import Box from "@mui/joy/Box";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";

import Button from "@mui/joy/Button";
import { Label } from "../api";
import LabelsTableHeaderWithInfoIcon from "./LabelsTableHeaderWithInfoIcon";
import { LabelsTableImplementationProps } from "./LabelsTableImplementationProps";
import PopularityBar from "./PopularityBar";
import getSpotifyPlaylistUrl from "./getSpotifyPlaylistUrl";
import getStreamsRangeText from "./getStreamsRangeText";

const LabelsTableMobile = ({ labels }: LabelsTableImplementationProps) => {
  return (
    <Grid container spacing={1}>
      {labels === undefined
        ? null
        : labels.labels.map((label) => (
            <Grid className="lofi-label-row" id={label.name} xs={12}>
              <Sheet sx={{ borderRadius: 4, p: 1 }}>
                <MobileLabelRow label={label} />
              </Sheet>
            </Grid>
          ))}
    </Grid>
  );
};

interface MobileLabelRowProps {
  label: Label;
}

const MobileLabelRow = ({ label }: MobileLabelRowProps) => {
  return (
    <Grid alignItems="center" container spacing={2} xs={12}>
      <Grid
        alignItems="center"
        display="flex"
        sx={{
          "& img": {
            borderRadius: 4,
            height: "100%",
            objectFit: "contain",
            width: "100%",
          },
        }}
        xs={3}
      >
        <img alt={`${label.name}`} src={label.imageUrl} />
      </Grid>
      <Grid
        container
        spacing={0}
        sx={(theme) => ({ fontSize: theme.fontSize.sm })}
        xs={9}
      >
        <Grid
          sx={(theme) => ({
            color: theme.palette.text.primary,
            fontSize: theme.fontSize.md,
            fontWeight: theme.fontWeight.xl,
          })}
          xs={12}
        >
          <Box alignItems="center" display="flex" justifyContent="space-between">
            {label.name}
            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <Button
                component="a"
                href={getSpotifyPlaylistUrl(label.playlistId)}
                size="sm"
                startDecorator={<OpenInNew />}
                sx={{
                  fontSize: (theme) => theme.fontSize.xs,
                  mb: -4,
                  mt: -4,
                  p: 0,
                }}
                variant="plain"
              >
                Spotify
              </Button>
            </Box>
          </Box>
        </Grid>
        <Grid xs={12}>
          <MobileLabelMetric
            left={
              <LabelsTableHeaderWithInfoIcon
                header="Popularity"
                info={
                  <>
                    <div>
                      Metric computed and made public by Spotify. Ranging from 0 to 100,
                      it represents how much a track has been listened to recently.
                    </div>
                    <div>Averaged over tracks released in the past 6 months.</div>
                  </>
                }
              />
            }
            right={
              <PopularityBar height={8} max={100} value={label.popularity} width={50} />
            }
          />
        </Grid>
        <Grid xs={12}>
          <MobileLabelMetric
            left={
              <>
                <span>Tracks </span>
                <span>(past 6 months)</span>
              </>
            }
            right={label.tracks}
          />
        </Grid>
        <Grid xs={12}>
          <MobileLabelMetric
            left={
              <LabelsTableHeaderWithInfoIcon
                header="Streams"
                info={
                  <>
                    <div>Estimated number of monthly streams per track.</div>
                    <div>This is just an estimation, use with caution!</div>
                    <div>Averaged over tracks released in the past 6 months.</div>
                  </>
                }
              />
            }
            right={getStreamsRangeText(label.streams)}
          />
        </Grid>
      </Grid>
    </Grid>
  );
};

interface MobileLabelMetricProps {
  left: ReactNode;
  right: ReactNode;
}

const MobileLabelMetric = ({ left, right }: MobileLabelMetricProps) => (
  <Box display="flex" justifyContent="space-between">
    <Box sx={{ color: (theme) => theme.palette.text.tertiary }}>{left}</Box>
    <Box sx={{ color: (theme) => theme.palette.text.primary }}>{right}</Box>
  </Box>
);

export default LabelsTableMobile;
