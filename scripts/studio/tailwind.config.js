/** Tailwind config for SuperWand Studio's stylesheet. Rebuild with ./build_css.sh */
module.exports = {
  content: {
    relative: true,
    files: ["../../src/superwand/studio/templates/**/*.html"],
  },
  theme: { extend: {} },
  plugins: [],
};
