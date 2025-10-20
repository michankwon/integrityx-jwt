import { NextApiRequest, NextApiResponse } from "next";

interface RequestRecord {
  [key: string]: number[];
}

const TIME_WINDOW = 60 * 60 * 1000;

const rateLimit = (limit: number) => {
  let requests: RequestRecord = {};
  return (req: NextApiRequest, res: NextApiResponse, next: Function) => {
    const now: number = Date.now();
    const ip: string = (
      req.headers["x-forwarded-for"] ||
      req.connection.remoteAddress ||
      ""
    ).toString();

    if (!requests[ip]) {
      requests[ip] = [];
    }
    requests[ip].push(now);

    requests[ip] = requests[ip].filter(
      (timestamp: number) => now - timestamp < TIME_WINDOW
    );

    if (requests[ip].length > limit) {
      res
        .status(429)
        .json({ message: "Too many requests. Please try again later." });
    } else {
      next();
    }
  };
};

export default rateLimit;
