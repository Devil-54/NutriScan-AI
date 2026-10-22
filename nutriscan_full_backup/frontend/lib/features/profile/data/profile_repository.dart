import 'profile_model.dart';
import 'profile_remote_datasource.dart';

class ProfileRepository {
  ProfileRepository(this._remote);
  final ProfileRemoteDatasource _remote;

  Future<FullProfileModel> getProfile() => _remote.getProfile();
  Future<HealthProfileModel> updateProfile(HealthProfileModel profile) => _remote.updateProfile(profile);
}
