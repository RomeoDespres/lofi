import Box from "@mui/joy/Box";
import Table from "@mui/joy/Table";
import LabelsTableHeaderWithInfoIcon from "./LabelsTableHeaderWithInfoIcon";
import { LabelsTableImplementationProps } from "./LabelsTableImplementationProps";
import PopularityBar from "./PopularityBar";
import getSpotifyPlaylistUrl from "./getSpotifyPlaylistUrl";
import getStreamsRangeText from "./getStreamsRangeText";
import SpotifyLogo from "./static/spotify.png";

const LabelsTableDesktop = ({ labels }: LabelsTableImplementationProps) => {
  return (
    <Table
      sx={(theme) => ({
        borderRadius: 4,
        color: theme.palette.neutral[400],
        fontSize: theme.typography["body-lg"].fontSize,
        "& th": { bgcolor: theme.palette.background.level1, pb: 2, pt: 2 },
        "& td": { pb: 1, pt: 1 },
        "& thead th:first-child": {
          borderTopLeftRadius: 8,
          color: theme.palette.text.icon,
          fontSize: theme.typography["body-sm"].fontSize,
          pl: 2,
          textAlign: "center",
          verticalAlign: "middle",
          width: "2.5rem",
        },
        "& thead th:last-child": { borderTopRightRadius: 8, pr: 2 },
        "& thead th:nth-child(6)": { width: "8%" },
        "& td:nth-child(1)": {
          color: theme.palette.text.icon,
          fontSize: theme.typography["body-sm"].fontSize,
          pl: 2,
          textAlign: "center",
        },
        // "& td:nth-child(6)": {
        //   textAlign: "center",
        // },
        "& td:nth-child(2)": {
          fontWeight: theme.fontWeight.md,
        },
        "& tr > *:not(:first-child, :nth-child(2))": {
          textAlign: "right",
        },
        "& tr:hover": {
          bgcolor: theme.palette.background.level2,
          color: theme.palette.neutral[300],
        },
        "& td:last-child": { opacity: 0.7, pr: 4 },
      })}
    >
      <thead>
        <tr>
          <th>#</th>
          <th>Label</th>
          <th>
            <LabelsTableHeaderWithInfoIcon
              header="Tracks"
              info="Number of tracks released in the past 6 months"
            />
          </th>
          <th>
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
          </th>
          <th>
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
          </th>
          <th>Listen</th>
        </tr>
      </thead>
      <tbody>
        {labels === undefined
          ? null
          : labels.labels.map((label, index) => (
              <tr>
                <td width="1px">{index + 1}</td>
                <td>
                  <Box
                    alignItems="center"
                    display="flex"
                    gap={2}
                    sx={{ "& img": { borderRadius: 4 } }}
                  >
                    <img alt={`${label.name}`} height={50} src={label.imageUrl} />
                    {label.name}
                  </Box>
                </td>
                <td>{label.tracks}</td>
                <td>{getStreamsRangeText(label.streams)}</td>
                <td>
                  <Box display="flex" justifyContent="flex-end">
                    <PopularityBar height={8} value={label.popularity} width={50} />
                  </Box>
                </td>
                <td>
                  <a
                    href={getSpotifyPlaylistUrl(label.playlistId)}
                    rel="noreferrer"
                    target="_blank"
                  >
                    <img
                      className="spotify-logo"
                      alt="Spotify logo"
                      height={25}
                      src={SpotifyLogo}
                    />
                  </a>
                </td>
              </tr>
            ))}
      </tbody>
    </Table>
  );
};

export default LabelsTableDesktop;
