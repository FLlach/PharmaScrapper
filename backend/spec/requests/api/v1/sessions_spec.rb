require 'swagger_helper'

RSpec.describe 'api/v1/sessions', type: :request do
  path '/api/v1/login' do
    post('create session') do
      tags 'Sessions'
      consumes 'application/json'
      produces 'application/json'
      parameter name: :credentials, in: :body, schema: {
        type: :object,
        properties: {
          email_address: { type: :string },
          password: { type: :string }
        },
        required: [ 'email_address', 'password' ]
      }

      response(200, 'successful') do
        let!(:user) { User.create!(email_address: 'test@example.com', password: 'password', role: 'standard') }
        let(:credentials) { { email_address: 'test@example.com', password: 'password' } }

        schema type: :object, properties: {
          message: { type: :string },
          user: {
            type: :object,
            properties: {
              id: { type: :integer },
              email: { type: :string },
              name: { type: :string, nullable: true },
              role: { type: :string }
            }
          }
        }
        run_test!
      end

      response(401, 'unauthorized') do
        let!(:user) { User.create!(email_address: 'test@example.com', password: 'password', role: 'standard') }
        let(:credentials) { { email_address: 'test@example.com', password: 'wrongpassword' } }

        schema type: :object, properties: {
          error: { type: :string }
        }
        run_test!
      end
    end
  end

  path '/api/v1/logout' do
    delete('delete session') do
      tags 'Sessions'
      produces 'application/json'

      response(200, 'successful') do
        let!(:user) { User.create!(email_address: 'test@example.com', password: 'password', role: 'standard') }

        before do
          post '/api/v1/login', params: { email_address: 'test@example.com', password: 'password' }
        end

        schema type: :object, properties: {
          message: { type: :string }
        }
        run_test!
      end

      response(401, 'unauthorized') do
        # Testing logout without a session
        schema type: :object, properties: {
          error: { type: :string }
        }
        run_test!
      end
    end
  end
end
