require 'rails_helper'

RSpec.describe "Api::V1::Sessions", type: :request do
  let(:user) { User.create!(email_address: "test@example.com", password: "password", name: "Test User") }

  describe "POST /api/v1/login" do
    context "with valid credentials" do
      it "creates a session and returns a success response" do
        post api_v1_login_path, params: { email_address: user.email_address, password: "password" }

        expect(response).to have_http_status(:ok)
        expect(JSON.parse(response.body)).to eq(
          "message" => "Logged in successfully",
          "user" => {
            "id" => user.id,
            "email" => user.email_address,
            "name" => user.name,
            "role" => user.role
          }
        )
      end
    end

    context "with invalid credentials" do
      it "returns an unauthorized response" do
        post api_v1_login_path, params: { email_address: user.email_address, password: "wrong_password" }

        expect(response).to have_http_status(:unauthorized)
        expect(JSON.parse(response.body)).to eq({ "error" => "Try another email address or password." })
      end
    end
  end

  describe "DELETE /api/v1/logout" do
    before do
      # Login to create a session
      post api_v1_login_path, params: { email_address: user.email_address, password: "password" }
    end

    it "terminates the session and returns a success response" do
      delete api_v1_logout_path

      expect(response).to have_http_status(:ok)
      expect(JSON.parse(response.body)).to eq({ "message" => "Logged out successfully" })
    end
  end
end
