import Table from "@mui/joy/Table";
import { useEffect, useState } from "react";
import { DefaultService, Labels } from "./api";
import SpotifyLogo from "./static/spotify.png";
import toKMB from "./toKMB";

const LabelsTable = () => {
  const [labels, setLabels] = useState<Labels>();

  useEffect(() => {
    DefaultService.getLabels().then(setLabels);
  }, []);

  return (
    <Table
      sx={(theme) => ({
        color: theme.palette.neutral[400],
        // "--joy-palette-background-level2": theme.palette.background.level1,
        fontSize: theme.typography["body-lg"].fontSize,
        "& thead th:nth-child(1)": {
          color: theme.palette.text.icon,
          fontSize: theme.typography["body-sm"].fontSize,
          textAlign: "center",
          verticalAlign: "middle",
          width: "2rem",
        },
        "& thead th:nth-child(6)": { width: "4rem" },
        "& td:nth-child(1)": {
          color: theme.palette.text.icon,
          fontSize: theme.typography["body-sm"].fontSize,
          textAlign: "center",
        },
        "& td:nth-child(6)": {
          textAlign: "center",
        },
        "& td:nth-child(2)": {
          fontWeight: theme.fontWeight.xl,
        },
        "& tr > *:not(:first-child, :nth-child(2), :nth-child(6))": {
          textAlign: "right",
        },
        "& tr:hover": {
          bgcolor: theme.palette.background.level2,
          color: theme.palette.neutral[300],
        },
        "& img": { opacity: 0.7 },
      })}
    >
      <thead>
        <tr>
          <th>#</th>
          <th>Label</th>
          <th>Tracks</th>
          <th>Streams</th>
          <th>Popularity</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {labels === undefined
          ? null
          : labels.labels.map((label, index) => (
              <tr>
                <td width="1px">{index + 1}</td>
                <td>{label.name}</td>
                <td>{label.tracks}</td>
                <td>
                  {toKMB(label.streams.min)} – {toKMB(label.streams.max)}
                </td>
                <td>{label.popularity} / 100</td>
                <td>
                  <a
                    href={`https://open.spotify.com/playlist/${label.playlistId}`}
                    rel="noreferrer"
                    target="_blank"
                  >
                    <img alt="Spotify logo" height={25} src={SpotifyLogo} />
                  </a>
                </td>
              </tr>
            ))}
      </tbody>
    </Table>
  );
};

export default LabelsTable;
