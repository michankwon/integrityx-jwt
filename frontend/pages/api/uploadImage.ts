import AWS from "aws-sdk";
import { NextApiRequest, NextApiResponse } from "next";
import sharp from "sharp";
import rateLimit from "@/middleware/rateLimiter";

AWS.config.update({
  accessKeyId: process.env.NEXT_PUBLIC_AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY,
  region: process.env.NEXT_PUBLIC_AWS_REGION,
});

const s3 = new AWS.S3();

const rateLimiter = rateLimit(100);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  await new Promise((resolve) => rateLimiter(req, res, resolve));

  if (res.headersSent) {
    return;
  }

  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { imageName, image } = req.body;

  if (!imageName || !image) {
    return res.status(400).json({ error: "Image name and image are required" });
  }

  const allowedFileTypes = ["image/jpeg", "image/png", "image/gif"];
  const fileType = image.split(";")[0].split(":")[1];

  if (!allowedFileTypes.includes(fileType)) {
    return res.status(400).json({ error: "Unsupported file type" });
  }

  const imageBuffer = Buffer.from(image.split(",")[1], "base64");

  try {
    const resizedImageBuffer = await sharp(imageBuffer).resize({ width: 1024 }).toBuffer();

    const key = `${imageName}-${Date.now()}`;

    const params = {
      Bucket: process.env.NEXT_PUBLIC_AWS_S3_BUCKET,
      Key: key,
      Body: resizedImageBuffer,
      ContentType: fileType,
    };

    await s3.upload(params as AWS.S3.Types.PutObjectRequest).promise();

    const imageUrl = `https://${process.env.NEXT_PUBLIC_AWS_S3_BUCKET}.s3.${process.env.NEXT_PUBLIC_AWS_REGION}.amazonaws.com/${key}`;

    res.status(200).json({ message: "Image uploaded successfully", imageUrl });
  } catch (error: any) {
    console.error("Error uploading image:", error);

    if (error.code === "EntityTooLarge") {
      return res.status(413).json({ error: "The image is too large to upload." });
    }

    let errorMessage = "Failed to upload image.";
    if (error.message && error.message.includes("unsupported image format")) {
      errorMessage = "The image format is not supported.";
      return res.status(400).json({ error: errorMessage });
    } else if (error.message && error.message.includes("Input buffer contains unsupported image format")) {
      errorMessage = "The input buffer contains an unsupported image format.";
      return res.status(400).json({ error: errorMessage });
    } else if (error.message && error.message.includes("not a valid image")) {
      errorMessage = "The uploaded file is not a valid image.";
      return res.status(400).json({ error: errorMessage });
    }

    res.status(500).json({ error: errorMessage });
  }
}
