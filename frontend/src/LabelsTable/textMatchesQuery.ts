const textMatchesQuery = (text: string, query: string) => {
  const preprocess = (s: string) =>
    s.toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()\s]/g, "");
  return preprocess(text).includes(preprocess(query));
};

export default textMatchesQuery;
