const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: __dirname,
  },
  output: "standalone",
};
module.exports = nextConfig;
