import { SassString } from 'sass';

export default {
  'get-parlassets-url()': () => {
    return new SassString(process.env.VITE_PARLASSETS_URL ?? '');
  },
  'fs-readFile($filePath)': () => {
    // this is only used in parlassets, noop here for compile compatibility
    return new SassString('');
  },
  'encode-svg($svg)': () => {
    // this is only used in parlassets, noop here for compile compatibility
    return new SassString('');
  },
  'str-replace($str, $find: "", $replace: "")': () => {
    // this is only used in parlassets, noop here for compile compatibility
    return new SassString('');
  },
};
