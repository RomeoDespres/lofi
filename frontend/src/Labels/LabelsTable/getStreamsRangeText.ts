import { StreamsRange } from "../../api";
import toKMB from "./toKMB";

const getStreamsRangeText = (streams: StreamsRange) =>
  `${toKMB(streams.min)} – ${toKMB(streams.max)}`;

export default getStreamsRangeText;
