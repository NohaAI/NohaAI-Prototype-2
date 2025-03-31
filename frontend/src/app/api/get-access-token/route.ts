export async function POST() {
    try {
      const baseApiUrl = "https://api.heygen.com";
  
      const res = await fetch(`${baseApiUrl}/v1/streaming.create_token`, {
        method: "POST",
        headers: {
          "x-api-key": "ZjhkNGFkYzhhYjBmNGVmZGEwNzZjNDk2ZjE0ZmM3MGUtMTc0MjgwOTU3OQ==",
        },
      });
  
      const data = await res.json();
      return new Response(data.data.token, {
        status: 200,
      });
    } catch (error) {
      console.error("Error retrieving access token:", error);
  
      return new Response("Failed to retrieve access token", {
        status: 500,
      });
    }
}