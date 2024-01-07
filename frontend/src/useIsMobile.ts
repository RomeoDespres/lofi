import useWindowDimensions from "./useWindowDimensions";

const useIsMobile = () => useWindowDimensions().width <= 900;

export default useIsMobile;
