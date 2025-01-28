import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import { Palette } from "@vibrant/color";
import { Vibrant } from "node-vibrant/browser";
import React from "react";
import { NavLink, useParams } from "react-router";
import {
  Artist,
  ArtistIndex,
  ArtistTrackAlbum,
  ArtistTrackArtist,
  BasicLabel,
  DefaultService,
} from "../api";
import SpotifyLogo from "../Labels/LabelsTable/static/spotify.png";
import textMatchesQuery from "../Labels/LabelsTable/textMatchesQuery";
import Page from "../Page";
import useIsMobile from "../useIsMobile";
import ArtistPageAccordion from "./ArtistPageAccordion";

export default function Artists() {
  const [artist, setArtist] = React.useState<Artist>();
  const [artists, setArtists] = React.useState<ArtistIndex["artists"]>([]);
  const [filteredArtists, setFilteredArtists] = React.useState<ArtistIndex["artists"]>(
    []
  );
  const [vibrantPalette, setVibrantPalette] = React.useState<Palette>();

  const { artistId } = useParams<{ artistId: string }>();
  const isMobile = useIsMobile();

  React.useEffect(() => {
    if (artistId === undefined) {
      setArtist(undefined);
      return;
    }

    DefaultService.getArtist(artistId).then((artist) =>
      artist.imageUrlL === null
        ? setArtist(artist)
        : Vibrant.from(artist.imageUrlL)
            .getPalette()
            .then((palette) => {
              setVibrantPalette(palette);
              setArtist(artist);
            })
    );
  }, [artistId]);

  const topCollaborator = artist === undefined ? null : getTopCollaborator(artist);

  React.useEffect(() => {
    DefaultService.getArtists().then((index) => setArtists(index.artists));
  }, []);
  console.log(artist?.tracks);
  return (
    <Page
      onSearch={(query) =>
        setFilteredArtists(
          query.length > 2
            ? artists.filter((artist) => textMatchesQuery(artist.name, query))
            : []
        )
      }
      pageTitle={
        artist === undefined || isMobile ? undefined : `lofi artists / ${artist.name}`
      }
      title="lofi artists"
      titleColor={vibrantPalette?.LightMuted?.hex}
      titleLink="/artists"
    >
      {artist === undefined || filteredArtists.length > 0 ? (
        <Grid
          container
          spacing={{ sm: 2, xs: 1 }}
          sx={{
            "& img.artist-image": {
              clipPath: "circle()",
              height: 50,
              objectFit: "contain",
              width: 50,
            },
          }}
        >
          {filteredArtists.length > 0 ? null : (
            <Box borderRadius={4} display="flex" justifyContent="center" width="100%">
              <Typography color="neutral" sx={{ padding: 4 }}>
                Use the search box to select an artist.
              </Typography>
            </Box>
          )}
          {filteredArtists.map((artist) => (
            <Grid md={4} lg={3} xs={12}>
              <NavLink
                to={`/artists/${artist.id}`}
                onClick={() => setFilteredArtists([])}
                style={{ textDecoration: "none" }}
              >
                <Sheet
                  sx={{
                    borderRadius: 4,
                    cursor: "pointer",
                    p: 1,
                    "&:hover": { bgcolor: (theme) => theme.palette.background.tooltip },
                  }}
                >
                  <Box alignItems="center" display="flex" gap={2}>
                    <img
                      alt={`${artist.name}`}
                      className="artist-image"
                      src={artist.imageUrlS ?? "DefaultArtistImage"}
                    />
                    {artist.name}
                  </Box>
                </Sheet>
              </NavLink>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box display="flex" flexDirection="column" gap={2}>
          <Box
            borderRadius={isMobile ? 4 : 8}
            bgcolor={(theme) => theme.palette.background.level1}
            display="flex"
            flexDirection="column"
            gap={2}
            p={2}
          >
            <Box alignItems="center" display="flex" gap={2}>
              <img
                alt={`${artist.name}`}
                src={artist.imageUrlL ?? "DefaultArtistImage"}
                style={{ clipPath: "circle()" }}
                width={90}
              />
              <Box display="flex" flexDirection="column" gap={1} mt={-1}>
                <Typography
                  level="h2"
                  sx={{ fontSize: 28, color: vibrantPalette?.LightMuted?.hex }}
                >
                  {artist.name}
                </Typography>
                <a
                  href={`https://open.spotify.com/artist/${artist.id}`}
                  target="_blank"
                >
                  <Button
                    sx={{
                      backgroundColor: vibrantPalette?.DarkMuted?.hex,
                      "&:hover": { backgroundColor: vibrantPalette?.LightMuted?.hex },
                    }}
                  >
                    <Box alignItems="center" display="flex" gap={1}>
                      <img width={22} src={SpotifyLogo} />
                      Listen on Spotify
                    </Box>
                  </Button>
                </a>
              </Box>
            </Box>
            <Box>
              First tracked release:{" "}
              {artist.tracks.length > 0
                ? new Date(
                    artist.tracks.reduce((acc, t) =>
                      t.album.releaseDate < acc.album.releaseDate ? t : acc
                    )?.album.releaseDate ?? undefined
                  ).toLocaleDateString("en-us", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })
                : "None"}
            </Box>
            <Box>Total tracks: {new Set(artist.tracks.map((t) => t.isrc)).size}</Box>
            <Box>
              Tracks in the past year:{" "}
              {
                new Set(
                  artist.tracks
                    .filter((t) => new Date(t.album.releaseDate) >= twelveMonthsAgo())
                    .map((t) => t.isrc)
                ).size
              }
            </Box>
            <Box>
              Top collaborator:{" "}
              {topCollaborator === null ? (
                "None"
              ) : (
                <>
                  <NavLink
                    to={`/artists/${topCollaborator[1].id}`}
                    style={{ textDecoration: "none" }}
                  >
                    {topCollaborator[1].name}
                  </NavLink>{" "}
                  ({topCollaborator[0]} tracks)
                </>
              )}
            </Box>
          </Box>
          <Grid container spacing={2}>
            <Grid xs={12} md={4}>
              <ArtistPageAccordion
                color={vibrantPalette?.LightMuted?.hex}
                title="Tracks by label"
              >
                <Table
                  aria-label="Tracks by label"
                  sx={(theme) => ({
                    borderRadius: 4,
                    color: theme.palette.neutral[400],
                    fontSize: theme.fontSize.md,
                    "& th": { bgcolor: theme.palette.background.level1, pb: 2, pt: 2 },
                    "& td": { pb: 1, pt: 1 },
                    "& thead th:first-child": {
                      borderTopLeftRadius: 8,
                      pl: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                      width: "80%",
                    },
                    "& thead th:nth-child(2)": {
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& thead th:last-child": {
                      borderTopRightRadius: 8,
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& td:nth-child(1)": { pl: { sm: 2, xs: 1 } },
                    "& td:nth-child(2)": {
                      fontWeight: theme.fontWeight.md,
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                    },
                    "& tr:hover": {
                      bgcolor: theme.palette.background.level2,
                      color: theme.palette.neutral[300],
                    },
                  })}
                >
                  <thead>
                    <tr>
                      <th>Label</th>
                      <th>Tracks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getTopLabels(artist).map(({ label, count }) => (
                      <tr>
                        <td>
                          <Box display="flex" alignItems="center" gap={1}>
                            <img
                              src={label.playlist.imageUrl}
                              width={30}
                              style={{ borderRadius: 2 }}
                            />
                            {label.name}
                          </Box>
                        </td>
                        <td>{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </ArtistPageAccordion>
            </Grid>
            <Grid xs={12} md={4}>
              <ArtistPageAccordion
                color={vibrantPalette?.LightMuted?.hex}
                title="Tracks by collaborator"
              >
                <Table
                  aria-label="Tracks by collaborator"
                  sx={(theme) => ({
                    borderRadius: 4,
                    color: theme.palette.neutral[400],
                    fontSize: theme.fontSize.md,
                    "& th": { bgcolor: theme.palette.background.level1, pb: 2, pt: 2 },
                    "& td": { pb: 1, pt: 1 },
                    "& thead th:first-child": {
                      borderTopLeftRadius: 8,
                      pl: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                      width: "80%",
                    },
                    "& thead th:nth-child(2)": {
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& thead th:last-child": {
                      borderTopRightRadius: 8,
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& td:nth-child(1)": { pl: { sm: 2, xs: 1 } },
                    "& td:nth-child(2)": {
                      fontWeight: theme.fontWeight.md,
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                    },
                    "& tr:hover": {
                      bgcolor: theme.palette.background.level2,
                      color: theme.palette.neutral[300],
                    },
                  })}
                >
                  <thead>
                    <tr>
                      <th>Collaborator</th>
                      <th>Tracks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getTopCollaborators(artist).map(({ artist, count }) => (
                      <tr>
                        <td>
                          <NavLink
                            to={`/artists/${artist.id}`}
                            style={{ color: "inherit", textDecoration: "none" }}
                          >
                            <Box display="flex" alignItems="center" gap={1}>
                              <img
                                src={artist.imageUrlS ?? ""}
                                width={30}
                                style={{ clipPath: "circle()" }}
                              />
                              {artist.name}
                            </Box>
                          </NavLink>
                        </td>
                        <td>{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </ArtistPageAccordion>
            </Grid>
            <Grid xs={12} md={4}>
              <ArtistPageAccordion
                color={vibrantPalette?.LightMuted?.hex}
                title="Discography"
              >
                <Table
                  aria-label="Tracks by label"
                  sx={(theme) => ({
                    borderRadius: 4,
                    color: theme.palette.neutral[400],
                    fontSize: theme.fontSize.md,
                    "& th": { bgcolor: theme.palette.background.level1, pb: 2, pt: 2 },
                    "& td": { pb: 1, pt: 1 },
                    "& thead th:first-child": {
                      borderTopLeftRadius: 8,
                      pl: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                      width: "80%",
                    },
                    "& thead th:nth-child(2)": {
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& thead th:last-child": {
                      borderTopRightRadius: 8,
                      pr: { sm: 2, xs: 1 },
                      verticalAlign: "middle",
                    },
                    "& td:nth-child(1)": { pl: { sm: 2, xs: 1 } },
                    "& td:nth-child(2)": {
                      fontWeight: theme.fontWeight.md,
                      textAlign: "right",
                      pr: { sm: 2, xs: 1 },
                    },
                    "& tr:hover": {
                      bgcolor: theme.palette.background.level2,
                      color: theme.palette.neutral[300],
                    },
                  })}
                >
                  <thead>
                    <tr>
                      <th>Release</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getDiscography(artist).map((album) => (
                      <tr>
                        <td>
                          <Box display="flex" alignItems="center" gap={1}>
                            <a
                              href={`https:/open.spotify.com/album/${album.id}`}
                              target="_blank"
                              style={{ color: "inherit", textDecoration: "none" }}
                            >
                              <img
                                src={album.imageUrlS ?? ""}
                                width={60}
                                style={{ borderRadius: 2 }}
                              />
                            </a>
                            <Box display="flex" flexDirection="column">
                              <Typography
                                sx={{ color: (theme) => theme.palette.text.primary }}
                              >
                                <a
                                  href={`https:/open.spotify.com/album/${album.id}`}
                                  target="_blank"
                                  style={{ color: "inherit", textDecoration: "none" }}
                                >
                                  {album.name}
                                </a>
                              </Typography>
                              <Typography fontSize={(theme) => theme.fontSize.sm}>
                                {album.artists.map((artist) => artist.name).join(", ")}
                              </Typography>
                              <Box
                                display="flex"
                                fontSize={(theme) => theme.fontSize.sm}
                                gap={0.5}
                                flexWrap="wrap"
                              >
                                <Typography>
                                  {album.type === "single" && album.trackCount > 2
                                    ? "EP"
                                    : toTitleCase(album.type)}
                                </Typography>
                                ·<Typography>{album.releaseDate}</Typography>·
                                <Typography>{album.label.name}</Typography>
                              </Box>
                            </Box>
                          </Box>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </ArtistPageAccordion>
            </Grid>
          </Grid>
        </Box>
      )}
    </Page>
  );
}

function toTitleCase(str: string) {
  return str.replace(
    /\w\S*/g,
    (text) => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase()
  );
}

function getTopLabels(artist: Artist) {
  const checkedIsrcs = new Set<string>();
  const labels = new Map<string, BasicLabel>();
  const tracksByLabel = new Map<string, number>();

  artist.tracks.forEach((track) => {
    if (checkedIsrcs.has(track.isrc)) return;

    checkedIsrcs.add(track.isrc);

    tracksByLabel.set(
      track.album.label.name,
      (tracksByLabel.get(track.album.label.name) ?? 0) + 1
    );

    labels.set(track.album.label.name, track.album.label);
  });

  const topLabels = [...tracksByLabel.entries()].map(([labelName, count]) => ({
    label: labels.get(labelName) as BasicLabel,
    count,
  }));

  topLabels.sort((a, b) =>
    a.count > b.count
      ? -1
      : a.count < b.count
      ? 1
      : a.label.name >= b.label.name
      ? 1
      : -1
  );

  return topLabels;
}

function getTopCollaborator(artist: Artist) {
  const checkedIsrcs = new Set<string>();
  const tracksByCollaborator = new Map<string, [number, ArtistTrackArtist]>();

  artist.tracks.forEach((track) => {
    if (checkedIsrcs.has(track.isrc)) return;

    checkedIsrcs.add(track.isrc);

    track.artists.forEach((collaborator) => {
      if (collaborator.id === artist.id) return;

      const count = tracksByCollaborator.has(collaborator.id)
        ? (tracksByCollaborator.get(collaborator.id) as [number, ArtistTrackArtist])[0]
        : 0;

      tracksByCollaborator.set(collaborator.id, [count + 1, collaborator]);
    });
  });

  return [null, ...tracksByCollaborator.values()].reduce(
    (acc, v) => (acc === null || v === null || v[0] >= acc[0] ? v : acc),
    null
  );
}

function getTopCollaborators(artist: Artist) {
  const checkedIsrcs = new Set<string>();
  const tracksByCollaborator = new Map<string, number>();
  const artistsById = new Map<string, ArtistTrackArtist>();

  artist.tracks.forEach((track) => {
    if (checkedIsrcs.has(track.isrc)) return;

    checkedIsrcs.add(track.isrc);

    track.artists.forEach((collaborator) => {
      if (collaborator.id === artist.id) return;

      tracksByCollaborator.set(
        collaborator.id,
        (tracksByCollaborator.get(collaborator.id) ?? 0) + 1
      );

      artistsById.set(collaborator.id, collaborator);
    });
  });

  const topCollaborators = [...tracksByCollaborator.entries()].map(
    ([artistId, count]) => ({
      artist: artistsById.get(artistId) as ArtistTrackArtist,
      count,
    })
  );

  topCollaborators.sort((a, b) =>
    a.count > b.count
      ? -1
      : a.count < b.count
      ? 1
      : a.artist.name >= b.artist.name
      ? 1
      : -1
  );

  return topCollaborators;
}

function getDiscography(artist: Artist) {
  const discography = new Map<string, ArtistTrackAlbum & { trackCount: number }>();

  artist.tracks.forEach((track) => {
    if (discography.has(track.album.id)) {
      (discography.get(track.album.id) as ArtistTrackAlbum & { trackCount: number })
        .trackCount++;
      return;
    }

    discography.set(track.album.id, { ...track.album, trackCount: 1 });
  });

  return [...discography.values()].sort((a1, a2) =>
    a1.releaseDate <= a2.releaseDate ? 1 : -1
  );
}

const twelveMonthsAgo = () => {
  const today = new Date();
  today.setFullYear(today.getFullYear() - 1);
  return today;
};
