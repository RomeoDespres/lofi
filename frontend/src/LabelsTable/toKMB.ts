const toKMB = (n: number) => {
  if (n === 0) return n.toString();
  const log1000 = Math.floor(Math.log(n) / Math.log(1000));
  if (log1000 > 3) return `${Math.round(n / 10 ** 9)}B`;
  const unit = ["", "k", "M", "B"][log1000];
  let value = (n / 10 ** (3 * log1000)).toFixed(2);
  let [intPart, decPart] = value.split(".");
  const intDigits = intPart.length;
  if (intDigits >= 3) value = intPart;
  else {
    if (intDigits === 2 || parseInt(decPart[1]) === 0) {
      decPart = decPart[0];
    }
    if (decPart.length === 1 && parseInt(decPart[0]) === 0) {
      decPart = "";
    }
    value = decPart.length === 0 ? intPart : intPart + "." + decPart;
  }
  return value + "" + unit;
};

export default toKMB;
